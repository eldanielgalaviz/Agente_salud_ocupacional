"""
Módulo de Detección de Fatiga CON CÁMARA REAL
Integrado con Prolog para inferencias
"""

import cv2
import time
import mysql.connector
from datetime import datetime
from pyswip import Prolog

class DetectorFatigaReal:
    def __init__(self, db_config, archivo_prolog='salud_ocupacional.pl'):
        """
        Inicializa el detector con cámara real
        """
        print("Inicializando detector de fatiga con cámara...")
        
        # Conexión a base de datos
        self.db = mysql.connector.connect(**db_config)
        self.cursor = self.db.cursor(dictionary=True)
        
        # Inicializar Prolog
        try:
            self.prolog = Prolog()
            self.prolog.consult(archivo_prolog)
            print("✓ Base de conocimiento Prolog cargada")
        except Exception as e:
            print(f"⚠️ Error cargando Prolog: {e}")
            self.prolog = None
        
        # Inicializar cámara
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            print("❌ No se pudo abrir la cámara")
            raise Exception("Cámara no disponible")
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        print("✓ Cámara inicializada (640x480)")
        
        # Cargar clasificadores de OpenCV
        cascade_path = cv2.data.haarcascades
        self.face_cascade = cv2.CascadeClassifier(cascade_path + 'haarcascade_frontalface_default.xml')
        self.eye_cascade = cv2.CascadeClassifier(cascade_path + 'haarcascade_eye.xml')
        print("✓ Clasificadores Haar cargados")
        
        # Variables de estado
        self.contador_parpadeos = 0
        self.ojos_cerrados_frames = 0
        self.umbral_parpadeo = 3
        self.postura_actual = "desconocida"
        
        # Métricas
        self.tiempo_inicio_minuto = time.time()
        self.parpadeos_ultimo_minuto = []
        
        # Sesión activa
        self.sesion_id = None
        
        print("✓ Detector de fatiga inicializado completamente\n")
    
    def establecer_sesion(self, sesion_id):
        """Establece la sesión activa"""
        self.sesion_id = sesion_id
        print(f"✓ Sesión establecida: {sesion_id}")
    
    def detectar_rostro_ojos(self, frame):
        """
        Detecta rostro y ojos en el frame
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detectar rostros
        rostros = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(100, 100)
        )
        
        if len(rostros) == 0:
            return None, [], frame
        
        # Tomar primer rostro
        (x, y, w, h) = rostros[0]
        cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        
        # Detectar ojos en región del rostro
        roi_gray = gray[y:y+h, x:x+w]
        roi_color = frame[y:y+h, x:x+w]
        
        ojos = self.eye_cascade.detectMultiScale(
            roi_gray,
            scaleFactor=1.1,
            minNeighbors=10,
            minSize=(20, 20)
        )
        
        # Dibujar ojos
        for (ex, ey, ew, eh) in ojos:
            cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (0, 255, 0), 2)
        
        return rostros[0], ojos, frame
    
    def detectar_parpadeo(self, ojos):
        """
        Detecta parpadeo basado en número de ojos visibles
        """
        if len(ojos) < 2:
            self.ojos_cerrados_frames += 1
        else:
            if self.ojos_cerrados_frames >= self.umbral_parpadeo:
                self.contador_parpadeos += 1
                print(f"Parpadeo detectado (Total: {self.contador_parpadeos})")
            self.ojos_cerrados_frames = 0
        
        return len(ojos) < 2
    
    def analizar_postura(self, rostro, altura_frame=480):
        """
        Analiza postura basándose en posición del rostro
        """
        if rostro is None:
            return "sin_deteccion"
        
        (x, y, w, h) = rostro
        centro_y = y + h/2
        
        # Detectar postura según posición vertical
        if centro_y < altura_frame * 0.35:
            postura = "cabeza_alta"
        elif centro_y > altura_frame * 0.65:
            postura = "cabeza_baja"
        else:
            # Detectar inclinación por ratio ancho/alto
            ratio = w / h
            if ratio < 0.7:
                postura = "cabeza_inclinada"
            else:
                postura = "correcta"
        
        self.postura_actual = postura
        return postura
    
    def calcular_nivel_fatiga(self):
        """
        Calcula nivel de fatiga cada minuto
        """
        tiempo_transcurrido = time.time() - self.tiempo_inicio_minuto
        
        if tiempo_transcurrido >= 60:
            frecuencia = self.contador_parpadeos
            self.parpadeos_ultimo_minuto.append(frecuencia)
            
            # Determinar nivel de fatiga visual
            # Normal: 15-20 parpadeos/minuto
            if frecuencia > 25:
                nivel_visual = "alto"
            elif frecuencia > 20:
                nivel_visual = "moderado"
            else:
                nivel_visual = "bajo"
            
            # Fatiga postural
            if self.postura_actual in ["cabeza_baja", "cabeza_inclinada"]:
                nivel_postural = "alto"
            elif self.postura_actual == "cabeza_alta":
                nivel_postural = "moderado"
            else:
                nivel_postural = "bajo"
            
            resultado = {
                'visual': nivel_visual,
                'postural': nivel_postural,
                'frecuencia_parpadeo': frecuencia
            }
            
            # Reiniciar contadores
            self.contador_parpadeos = 0
            self.tiempo_inicio_minuto = time.time()
            
            return resultado
        
        return None
    
    def actualizar_prolog(self, nivel_visual, nivel_postural):
        """
        Actualiza hechos dinámicos en Prolog
        """
        if self.prolog is None:
            return
        
        try:
            # Actualizar fatiga visual
            list(self.prolog.query("retractall(nivel_fatiga(visual, _))"))
            list(self.prolog.query(f"assertz(nivel_fatiga(visual, {nivel_visual}))"))
            
            # Actualizar fatiga postural
            list(self.prolog.query("retractall(nivel_fatiga(postural, _))"))
            list(self.prolog.query(f"assertz(nivel_fatiga(postural, {nivel_postural}))"))
            
            print(f"Prolog actualizado - Visual: {nivel_visual}, Postural: {nivel_postural}")
            
            # Consultar si hay fatiga general alta
            resultado = list(self.prolog.query("fatiga_general_alta"))
            if len(resultado) > 0:
                print("⚠️ Prolog detectó: FATIGA GENERAL ALTA")
                return True
            
        except Exception as e:
            print(f"❌ Error actualizando Prolog: {e}")
        
        return False
    
    def registrar_deteccion(self, tipo_fatiga, nivel, indicador):
        """
        Registra detección en base de datos
        """
        if self.sesion_id is None:
            return
        
        try:
            query = """
                INSERT INTO deteccion_fatiga 
                (sesion_id, tipo_fatiga, nivel_fatiga, indicador, 
                 frecuencia_parpadeo, postura_detectada)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            self.cursor.execute(query, (
                self.sesion_id,
                tipo_fatiga,
                nivel,
                indicador,
                self.contador_parpadeos,
                self.postura_actual
            ))
            self.db.commit()
            
        except Exception as e:
            print(f"❌ Error registrando: {e}")
    
    def agregar_info_frame(self, frame, rostro, ojos, postura):
        """
        Agrega información visual al frame
        """
        # Información de parpadeos
        cv2.putText(frame, f"Parpadeos: {self.contador_parpadeos}", 
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        # Información de postura
        color_postura = (0, 255, 0) if postura == "correcta" else (0, 0, 255)
        cv2.putText(frame, f"Postura: {postura}", 
                    (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color_postura, 2)
        
        # Estado de ojos
        estado_ojos = "Cerrados" if len(ojos) < 2 else "Abiertos"
        cv2.putText(frame, f"Ojos: {estado_ojos}", 
                    (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)
    
    def ejecutar_monitor_continuo(self):
        try:
            while True:
                ret, frame = self.cap.read()
                
                if not ret:
                    print("❌ Error capturando frame")
                    break
                
                # Detectar rostro y ojos
                rostro, ojos, frame_anotado = self.detectar_rostro_ojos(frame)
                
                # Detectar parpadeo
                self.detectar_parpadeo(ojos)
                
                # Analizar postura
                postura = self.analizar_postura(rostro)
                
                # Calcular niveles de fatiga (cada minuto)
                niveles = self.calcular_nivel_fatiga()
                
                if niveles:
                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Análisis de fatiga:")
                    print(f"Visual: {niveles['visual']} ({niveles['frecuencia_parpadeo']} parpadeos/min)")
                    print(f"Postural: {niveles['postural']} (Postura: {self.postura_actual})")
                    
                    # Actualizar Prolog
                    fatiga_alta = self.actualizar_prolog(
                        niveles['visual'],
                        niveles['postural']
                    )
                    
                    # Registrar en BD
                    self.registrar_deteccion('visual', niveles['visual'], 
                                        f"Parpadeos: {niveles['frecuencia_parpadeo']}/min")
                    self.registrar_deteccion('postural', niveles['postural'], 
                                        f"Postura: {self.postura_actual}")
                
                # Agregar información al frame
                self.agregar_info_frame(frame_anotado, rostro, ojos, postura)
                
                # Mostrar frame
                cv2.imshow('Monitor de Fatiga - Salud Ocupacional', frame_anotado)
                
                # Salir con 'q'
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                
        except KeyboardInterrupt:
            print("\n✓ Monitor detenido por el usuario")
        finally:
            self.cerrar()
    
    def cerrar(self):
        """
        Libera recursos
        """
        self.cap.release()
        cv2.destroyAllWindows()
        self.cursor.close()
        self.db.close()
        print("✓ Recursos liberados")

# ========================================
# EJECUCIÓN PRINCIPAL
# ========================================

if __name__ == "__main__":
    # Configuración
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',
        'database': 'salud_ocupacional'
    }
    
    # Obtener sesión activa
    try:
        conexion = mysql.connector.connect(**db_config)
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id FROM sesiones_trabajo WHERE estado = 'activa' ORDER BY id DESC LIMIT 1")
        sesion = cursor.fetchone()
        
        if not sesion:
            cursor.execute("""
                INSERT INTO sesiones_trabajo (usuario_id, fecha, hora_inicio, estado)
                VALUES (1, CURDATE(), CURTIME(), 'activa')
            """)
            conexion.commit()
            sesion_id = cursor.lastrowid
        else:
            sesion_id = sesion['id']
        
        cursor.close()
        conexion.close()
        
        # Crear detector
        detector = DetectorFatigaReal(db_config)
        detector.establecer_sesion(sesion_id)
        
        # Ejecutar monitor
        detector.ejecutar_monitor_continuo()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()