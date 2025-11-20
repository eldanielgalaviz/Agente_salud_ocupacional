"""
Módulo de Síntesis de Voz - VERSIÓN ROBUSTA
Reinicia el motor entre mensajes para mayor confiabilidad
"""

import pyttsx3
import time

class AsistenteVozRobusto:
    def __init__(self):
        """Inicializa configuración de voz"""
        self.velocidad = 150
        self.volumen = 1.0
        print("✓ Asistente de voz inicializado (modo robusto)")
    
    def hablar(self, texto):
        """
        Convierte texto a voz con motor independiente
        """
        try:
            print(f"🔊 Diciendo: {texto}")
            
            # Crear motor nuevo para cada mensaje
            engine = pyttsx3.init()
            engine.setProperty('rate', self.velocidad)
            engine.setProperty('volume', self.volumen)
            
            # Hablar
            engine.say(texto)
            engine.runAndWait()
            
            # Limpiar
            engine.stop()
            del engine
            
            # Pausa entre mensajes
            time.sleep(0.5)
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    # ========================================
    # MENSAJES DEL SISTEMA
    # ========================================
    
    def bienvenida(self):
        self.hablar("Bienvenido al sistema de salud ocupacional. Tu sesión ha comenzado.")
    
    def alerta_co2_alto(self, valor):
        self.hablar(f"Atención. Nivel de dióxido de carbono elevado: {valor} partes por millón.")
        time.sleep(1)
        self.hablar("Se recomienda mejorar la ventilación.")
    
    def alerta_ruido_alto(self, valor):
        self.hablar(f"Nivel de ruido elevado: {valor} decibeles.")
        time.sleep(1)
        self.hablar("Considera utilizar audífonos con cancelación de ruido.")
    
    def recordatorio_pausa(self, minutos):
        self.hablar(f"Has trabajado {minutos} minutos sin descanso.")
        time.sleep(1)
        self.hablar("Es momento de tomar una pausa de cinco minutos.")
    
    def alerta_fatiga_visual(self):
        self.hablar("Se han detectado signos de fatiga visual.")
        time.sleep(1)
        self.hablar("Descansa la vista mirando a lo lejos durante veinte segundos.")
    
    def alerta_fatiga_postural(self):
        self.hablar("Tu postura no es correcta.")
        time.sleep(1)
        self.hablar("Ajusta tu posición y realiza algunos estiramientos.")
    
    def despedida(self, minutos_totales):
        self.hablar(f"Sesión finalizada. Has trabajado {minutos_totales} minutos.")
        time.sleep(1)
        self.hablar("Que tengas un excelente día.")
    
    # ========================================
    # GUÍAS DE EJERCICIOS
    # ========================================
    
    def guiar_ejercicio_20_20_20(self):
        print("\n🎯 Iniciando ejercicio visual 20-20-20\n")
        
        self.hablar("Ejercicio visual veinte, veinte, veinte.")
        time.sleep(2)
        
        self.hablar("Aparta la mirada de la pantalla.")
        time.sleep(2)
        
        self.hablar("Busca un objeto a seis metros de distancia.")
        time.sleep(2)
        
        self.hablar("Concéntrate en ese objeto durante veinte segundos.")
        print("   [Esperando 20 segundos...]")
        time.sleep(20)
        
        self.hablar("Perfecto. Ejercicio completado.")
    
    def guiar_estiramiento_cuello(self):
        print("\n🎯 Iniciando estiramiento de cuello\n")
        
        self.hablar("Estiramiento de cuello.")
        time.sleep(2)
        
        self.hablar("Inclina lentamente tu cabeza hacia el hombro derecho.")
        time.sleep(3)
        
        self.hablar("Mantén cinco segundos.")
        time.sleep(5)
        
        self.hablar("Regresa al centro.")
        time.sleep(2)
        
        self.hablar("Ahora inclina hacia el hombro izquierdo.")
        time.sleep(3)
        
        self.hablar("Mantén cinco segundos.")
        time.sleep(5)
        
        self.hablar("Regresa al centro. Ejercicio completado.")

# ========================================
# PRUEBA DEL MÓDULO
# ========================================

if __name__ == "__main__":
    print("="*60)
    print("PRUEBA DEL ASISTENTE DE VOZ - VERSIÓN ROBUSTA")
    print("="*60 + "\n")
    
    asistente = AsistenteVozRobusto()
    
    print("1. Mensaje de bienvenida:")
    asistente.bienvenida()
    time.sleep(2)
    
    print("\n2. Alerta de CO2:")
    asistente.alerta_co2_alto(1250)
    time.sleep(2)
    
    print("\n3. Alerta de ruido:")
    asistente.alerta_ruido_alto(75)
    time.sleep(2)
    
    print("\n4. Alerta de fatiga visual:")
    asistente.alerta_fatiga_visual()
    time.sleep(2)
    
    print("\n5. Recordatorio de pausa:")
    asistente.recordatorio_pausa(60)
    time.sleep(2)
    
    print("\n6. Guía de ejercicio:")
    respuesta = input("\n¿Quieres probar la guía de ejercicio 20-20-20? (s/n): ")
    if respuesta.lower() == 's':
        asistente.guiar_ejercicio_20_20_20()
    
    print("\n✓ Prueba completada")