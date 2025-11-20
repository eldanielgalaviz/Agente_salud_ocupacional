"""
SISTEMA INTEGRADO DE SALUD OCUPACIONAL
Integra detector de fatiga con cámara + asistente de voz + ESP32 REAL
"""

import threading
import queue
import time
import sys
import requests
from detector_fatiga_real import DetectorFatigaReal
from asistente_voz import AsistenteVozRobusto

# Cola de eventos para comunicación entre componentes
cola_alertas = queue.Queue()

class ControladorESP32:
    """Clase para comunicarse con ESP32 vía API"""
    
    def __init__(self, api_url='http://localhost:3001', device_id='ESP32_ESCRITORIO_01'):
        self.api_url = api_url
        self.device_id = device_id
    
    def obtener_ultima_lectura_co2(self):
        """Obtiene la última lectura de CO2 desde la API"""
        try:
            response = requests.get(f"{self.api_url}/api/sensores/ultimas", timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'lecturas' in data:
                    if 'co2' in data['lecturas']:
                        return data['lecturas']['co2']['valor']
        except Exception as e:
            print(f"⚠️ Error obteniendo lectura CO2: {e}")
        return None
    
    def enviar_comando(self, accion, parametro=''):
        """Envía un comando al ESP32 vía API"""
        try:
            payload = {
                'device_id': self.device_id,
                'accion': accion,
                'parametro': parametro
            }
            response = requests.post(
                f"{self.api_url}/api/esp32/comando/enviar", 
                json=payload,
                timeout=5
            )
            if response.status_code == 200:
                print(f"✓ Comando enviado: {accion}")
                return True
        except Exception as e:
            print(f"⚠️ Error enviando comando: {e}")
        return False


class SistemaSaludOcupacional:
    def __init__(self, db_config):
        """
        Inicializa el sistema completo
        """
        print("="*60)
        print("SISTEMA INTEGRADO DE SALUD OCUPACIONAL")
        print("Con ESP32 + Sensores Reales")
        print("="*60)
        
        # Inicializar componentes
        self.asistente_voz = AsistenteVozRobusto()
        self.detector_fatiga = None
        self.controlador_esp32 = ControladorESP32()
        self.db_config = db_config
        
        # Control de threads
        self.corriendo = True
        self.thread_detector = None
        self.thread_procesador_alertas = None
        self.thread_monitor_co2 = None
        
        # Últimas alertas enviadas (para evitar repetir)
        self.ultima_alerta_visual = 0
        self.ultima_alerta_postural = 0
        self.ultima_alerta_co2 = 0
        self.intervalo_minimo_alertas = 120  # 2 minutos entre alertas del mismo tipo
        
        # Última lectura CO2
        self.ultimo_co2 = 0
        
        print("✓ Sistema inicializado\n")
    
    def iniciar(self):
        """
        Inicia todos los componentes del sistema
        """
        try:
            # Mensaje de bienvenida
            self.asistente_voz.bienvenida()
            time.sleep(2)
            
            # Obtener o crear sesión activa
            import mysql.connector
            conexion = mysql.connector.connect(**self.db_config)
            cursor = conexion.cursor(dictionary=True)
            
            cursor.execute("""
                SELECT id FROM sesiones_trabajo 
                WHERE estado = 'activa' 
                ORDER BY id DESC LIMIT 1
            """)
            sesion = cursor.fetchone()
            
            if not sesion:
                cursor.execute("""
                    INSERT INTO sesiones_trabajo (usuario_id, fecha, hora_inicio, estado)
                    VALUES (1, CURDATE(), CURTIME(), 'activa')
                """)
                conexion.commit()
                sesion_id = cursor.lastrowid
                print(f"✓ Nueva sesión creada: {sesion_id}")
            else:
                sesion_id = sesion['id']
                print(f"✓ Sesión existente: {sesion_id}")
            
            cursor.close()
            conexion.close()
            
            # Inicializar detector de fatiga
            self.detector_fatiga = DetectorFatigaReal(self.db_config)
            self.detector_fatiga.establecer_sesion(sesion_id)
            
            # Iniciar threads
            self.thread_detector = threading.Thread(
                target=self._ejecutar_detector,
                daemon=True
            )
            
            self.thread_procesador_alertas = threading.Thread(
                target=self._procesar_alertas,
                daemon=True
            )
            
            self.thread_monitor_co2 = threading.Thread(
                target=self._monitorear_co2,
                daemon=True
            )
            
            self.thread_detector.start()
            self.thread_procesador_alertas.start()
            self.thread_monitor_co2.start()
            
            print("\n" + "="*60)
            print("SISTEMA EN FUNCIONAMIENTO")
            print("="*60)
            print("✓ Detección de fatiga por cámara: ACTIVA")
            print("✓ Monitor de CO2 (ESP32): ACTIVO")
            print("✓ Asistente de voz: ACTIVO")
            print("="*60)
            print("Presiona 'q' en la ventana de la cámara para detener")
            print("="*60 + "\n")
            
            # Mantener el programa principal corriendo
            self.thread_detector.join()
            
        except KeyboardInterrupt:
            print("\n\n✓ Sistema detenido por el usuario")
            self.detener()
        except Exception as e:
            print(f"\n✗ Error en el sistema: {e}")
            import traceback
            traceback.print_exc()
            self.detener()
    
    def _monitorear_co2(self):
        """
        Thread que monitorea CO2 desde ESP32 vía API
        """
        print("✓ Monitor de CO2 iniciado\n")
        
        while self.corriendo:
            try:
                # Obtener lectura actual de CO2
                co2 = self.controlador_esp32.obtener_ultima_lectura_co2()
                
                if co2 is not None and co2 != self.ultimo_co2:
                    self.ultimo_co2 = co2
                    print(f"📊 CO2: {co2} ppm")
                    
                    # Generar alertas si es necesario
                    tiempo_actual = time.time()
                    
                    if co2 > 1200:
                        if tiempo_actual - self.ultima_alerta_co2 > self.intervalo_minimo_alertas:
                            cola_alertas.put({
                                'tipo': 'co2_alto',
                                'valor': co2
                            })
                            self.ultima_alerta_co2 = tiempo_actual
                
                # Esperar 15 segundos antes de siguiente lectura
                time.sleep(15)
                
            except Exception as e:
                print(f"⚠️ Error en monitor CO2: {e}")
                time.sleep(10)
    
    def _ejecutar_detector(self):
        """
        Thread que ejecuta el detector de fatiga
        """
        try:
            import cv2
            
            while self.corriendo:
                ret, frame = self.detector_fatiga.cap.read()
                
                if not ret:
                    print("✗ Error capturando frame")
                    break
                
                # Detectar rostro y ojos
                rostro, ojos, frame_anotado = self.detector_fatiga.detectar_rostro_ojos(frame)
                
                # Detectar parpadeo
                self.detector_fatiga.detectar_parpadeo(ojos)
                
                # Analizar postura
                postura = self.detector_fatiga.analizar_postura(rostro)
                
                # Calcular niveles de fatiga (cada minuto)
                niveles = self.detector_fatiga.calcular_nivel_fatiga()
                
                if niveles:
                    self._manejar_deteccion_fatiga(niveles)
                
                # Agregar información al frame
                self.detector_fatiga.agregar_info_frame(frame_anotado, rostro, ojos, postura)
                
                # Agregar info de CO2
                cv2.putText(frame_anotado, f"CO2: {self.ultimo_co2} ppm", 
                           (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
                
                # Mostrar frame
                cv2.imshow('Monitor de Fatiga - Salud Ocupacional', frame_anotado)
                
                # Salir con 'q'
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            self.corriendo = False
            
        except Exception as e:
            print(f"✗ Error en detector: {e}")
            import traceback
            traceback.print_exc()
            self.corriendo = False
    
    def _manejar_deteccion_fatiga(self, niveles):
        """
        Maneja las detecciones de fatiga y genera alertas de voz
        """
        from datetime import datetime
        
        tiempo_actual = time.time()
        
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Análisis de fatiga:")
        print(f"Visual: {niveles['visual']} ({niveles['frecuencia_parpadeo']} parpadeos/min)")
        print(f"Postural: {niveles['postural']} (Postura: {self.detector_fatiga.postura_actual})")
        
        # Actualizar Prolog
        fatiga_alta = self.detector_fatiga.actualizar_prolog(
            niveles['visual'],
            niveles['postural']
        )
        
        # Registrar en BD
        self.detector_fatiga.registrar_deteccion(
            'visual', 
            niveles['visual'], 
            f"Parpadeos: {niveles['frecuencia_parpadeo']}/min"
        )
        self.detector_fatiga.registrar_deteccion(
            'postural', 
            niveles['postural'], 
            f"Postura: {self.detector_fatiga.postura_actual}"
        )
        
        # Generar alertas de voz si es necesario
        if niveles['visual'] in ['alto', 'moderado']:
            if tiempo_actual - self.ultima_alerta_visual > self.intervalo_minimo_alertas:
                cola_alertas.put({
                    'tipo': 'fatiga_visual',
                    'nivel': niveles['visual'],
                    'frecuencia': niveles['frecuencia_parpadeo']
                })
                self.ultima_alerta_visual = tiempo_actual
        
        if niveles['postural'] in ['alto', 'moderado']:
            if tiempo_actual - self.ultima_alerta_postural > self.intervalo_minimo_alertas:
                cola_alertas.put({
                    'tipo': 'fatiga_postural',
                    'nivel': niveles['postural'],
                    'postura': self.detector_fatiga.postura_actual
                })
                self.ultima_alerta_postural = tiempo_actual
    
    def _procesar_alertas(self):
        """
        Thread que procesa la cola de alertas y activa el asistente de voz
        """
        while self.corriendo:
            try:
                alerta = cola_alertas.get(timeout=1)
                
                if alerta['tipo'] == 'fatiga_visual':
                    self.asistente_voz.alerta_fatiga_visual()
                    time.sleep(2)
                    print("\n¿Deseas realizar el ejercicio 20-20-20? (Automático en 5 seg)")
                    time.sleep(5)
                    self.asistente_voz.guiar_ejercicio_20_20_20()
                
                elif alerta['tipo'] == 'fatiga_postural':
                    self.asistente_voz.alerta_fatiga_postural()
                    time.sleep(2)
                    print("\n¿Deseas realizar estiramiento de cuello? (Automático en 5 seg)")
                    time.sleep(5)
                    self.asistente_voz.guiar_estiramiento_cuello()
                
                elif alerta['tipo'] == 'co2_alto':
                    self.asistente_voz.alerta_co2_alto(alerta['valor'])
                
                cola_alertas.task_done()
                
            except queue.Empty:
                continue
            except Exception as e:
                print(f"✗ Error procesando alerta: {e}")
    
    def detener(self):
        """
        Detiene todos los componentes
        """
        print("\n\nDeteniendo sistema...")
        self.corriendo = False
        
        if self.detector_fatiga:
            self.detector_fatiga.cerrar()
        
        import mysql.connector
        try:
            conexion = mysql.connector.connect(**self.db_config)
            cursor = conexion.cursor(dictionary=True)
            cursor.execute("""
                SELECT minutos_totales FROM sesiones_trabajo 
                WHERE estado = 'activa' 
                ORDER BY id DESC LIMIT 1
            """)
            sesion = cursor.fetchone()
            minutos = sesion['minutos_totales'] if sesion else 0
            cursor.close()
            conexion.close()
            
            self.asistente_voz.despedida(minutos)
        except:
            pass
        
        print("✓ Sistema detenido completamente\n")
        sys.exit(0)


# ========================================
# EJECUCIÓN PRINCIPAL
# ========================================

if __name__ == "__main__":
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'salud_ocupacional'
    }
    
    sistema = SistemaSaludOcupacional(db_config)
    sistema.iniciar()