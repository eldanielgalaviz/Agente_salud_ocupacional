"""
Módulo de Detección de Fatiga - VERSIÓN SIMULADA
Sin cámara real, con datos generados automáticamente
"""

import time
import random
import mysql.connector
from datetime import datetime

class DetectorFatigaSimulado:
    def __init__(self, db_config):
        """
        Inicializa el detector de fatiga simulado
        """
        # Conexión a base de datos
        self.db = mysql.connector.connect(**db_config)
        self.cursor = self.db.cursor(dictionary=True)
        
        # Variables de simulación
        self.parpadeos_por_minuto = 15
        self.postura_actual = "correcta"
        self.tiempo_inicio = time.time()
        
        # Sesión activa
        self.sesion_id = None
        
        print("✓ Detector de fatiga simulado inicializado")
    
    def establecer_sesion(self, sesion_id):
        """
        Establece la sesión activa para registrar detecciones
        """
        self.sesion_id = sesion_id
        print(f"✓ Sesión establecida: {sesion_id}")
    
    def simular_deteccion_fatiga(self):
        """
        Simula la detección de fatiga con variaciones aleatorias
        """
        tiempo_transcurrido = time.time() - self.tiempo_inicio
        
        # Simular aumento gradual de fatiga con el tiempo
        minutos = tiempo_transcurrido / 60
        
        # Fatiga visual (aumenta con el tiempo)
        if minutos < 30:
            self.parpadeos_por_minuto = random.randint(15, 20)
            nivel_visual = "bajo"
        elif minutos < 60:
            self.parpadeos_por_minuto = random.randint(20, 25)
            nivel_visual = "moderado"
        else:
            self.parpadeos_por_minuto = random.randint(25, 35)
            nivel_visual = "alto"
        
        # Fatiga postural (varía aleatoriamente)
        posturas = ["correcta", "correcta", "cabeza_baja", "cabeza_inclinada"]
        self.postura_actual = random.choice(posturas)
        
        if self.postura_actual == "correcta":
            nivel_postural = "bajo"
        elif self.postura_actual in ["cabeza_baja", "cabeza_inclinada"]:
            nivel_postural = "alto"
        else:
            nivel_postural = "moderado"
        
        # Fatiga cognitiva (basada en tiempo)
        if minutos < 45:
            nivel_cognitiva = "bajo"
        elif minutos < 90:
            nivel_cognitiva = "moderado"
        else:
            nivel_cognitiva = "alto"
        
        return {
            'visual': nivel_visual,
            'postural': nivel_postural,
            'cognitiva': nivel_cognitiva,
            'parpadeos': self.parpadeos_por_minuto,
            'postura': self.postura_actual
        }
    
    def registrar_deteccion(self, tipo_fatiga, nivel, indicador, datos_extra=None):
        """
        Registra detección de fatiga en la base de datos
        """
        if self.sesion_id is None:
            print("⚠️ No hay sesión activa")
            return
        
        try:
            query = """
                INSERT INTO deteccion_fatiga 
                (sesion_id, tipo_fatiga, nivel_fatiga, indicador, 
                 frecuencia_parpadeo, postura_detectada)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            
            frecuencia = datos_extra.get('parpadeos') if datos_extra else None
            postura = datos_extra.get('postura') if datos_extra else None
            
            self.cursor.execute(query, (
                self.sesion_id,
                tipo_fatiga,
                nivel,
                indicador,
                frecuencia,
                postura
            ))
            self.db.commit()
            
            print(f"📝 Fatiga {tipo_fatiga}: {nivel}")
            
        except Exception as e:
            print(f"❌ Error registrando fatiga: {e}")
    
    def analizar_y_registrar(self):
        """
        Realiza análisis completo y registra en base de datos
        """
        # Simular detección
        resultado = self.simular_deteccion_fatiga()
        
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Análisis de Fatiga:")
        print(f"  👁️  Visual: {resultado['visual']} (Parpadeos: {resultado['parpadeos']}/min)")
        print(f"  🧍 Postural: {resultado['postural']} (Postura: {resultado['postura']})")
        print(f"  🧠 Cognitiva: {resultado['cognitiva']}")
        
        # Registrar en base de datos
        self.registrar_deteccion(
            'visual',
            resultado['visual'],
            f"Frecuencia parpadeo: {resultado['parpadeos']}/min",
            resultado
        )
        
        self.registrar_deteccion(
            'postural',
            resultado['postural'],
            f"Postura: {resultado['postura']}",
            resultado
        )
        
        self.registrar_deteccion(
            'cognitiva',
            resultado['cognitiva'],
            "Análisis de tiempo de trabajo",
            resultado
        )
        
        return resultado
    
    def ejecutar_monitor_continuo(self, intervalo=60):
        """
        Ejecuta monitoreo continuo cada X segundos
        """
        print("\n" + "="*60)
        print("🎥 MONITOR DE FATIGA - MODO SIMULACIÓN")
        print("="*60)
        print(f"Análisis cada {intervalo} segundos")
        print("Presiona Ctrl+C para detener\n")
        
        try:
            while True:
                self.analizar_y_registrar()
                time.sleep(intervalo)
                
        except KeyboardInterrupt:
            print("\n\n✓ Monitor detenido por el usuario")
        finally:
            self.cerrar()
    
    def cerrar(self):
        """
        Cierra conexiones
        """
        self.cursor.close()
        self.db.close()
        print("✓ Detector de fatiga cerrado")

# ========================================
# EJECUCIÓN PRINCIPAL
# ========================================

if __name__ == "__main__":
    # Configuración de base de datos
    db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': '',  # Vacío para XAMPP
        'database': 'salud_ocupacional'
    }
    
    # Crear detector
    detector = DetectorFatigaSimulado(db_config)
    
    # Obtener sesión activa
    try:
        conexion = mysql.connector.connect(**db_config)
        cursor = conexion.cursor(dictionary=True)
        cursor.execute("SELECT id FROM sesiones_trabajo WHERE estado = 'activa' ORDER BY id DESC LIMIT 1")
        sesion = cursor.fetchone()
        
        if sesion:
            detector.establecer_sesion(sesion['id'])
            print(f"✓ Usando sesión activa: {sesion['id']}\n")
        else:
            print("⚠️ No hay sesión activa. Iniciando una nueva...")
            cursor.execute("""
                INSERT INTO sesiones_trabajo (usuario_id, fecha, hora_inicio, estado)
                VALUES (1, CURDATE(), CURTIME(), 'activa')
            """)
            conexion.commit()
            detector.establecer_sesion(cursor.lastrowid)
        
        cursor.close()
        conexion.close()
        
    except Exception as e:
        print(f"❌ Error obteniendo sesión: {e}")
        exit(1)
    
    # Ejecutar monitor (análisis cada 60 segundos)
    detector.ejecutar_monitor_continuo(intervalo=60)