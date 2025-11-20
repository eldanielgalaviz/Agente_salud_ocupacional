/**
* ESP32 - Sistema de Salud Ocupacional
* Sensores: MQ135 (CO2)
* Actuadores: Ventilador (Relé), LEDs
*/

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// ========================================
// CONFIGURACIÓN WiFi
// ========================================
const char* ssid = "TU_RED_WIFI";           // Cambiar por tu red
const char* password = "TU_PASSWORD_WIFI";   // Cambiar por tu contraseña

// ========================================
// CONFIGURACIÓN API
// ========================================
const char* apiURL = "http://192.168.1.100:3001"; // Cambiar por IP de tu PC
String deviceID = "ESP32_ESCRITORIO_01";

// ========================================
// PINES DE HARDWARE
// ========================================
const int PIN_MQ135 = 34;        // Pin analógico para sensor MQ135
const int PIN_RELE_VENTILADOR = 25;  // Pin digital para relé del ventilador
const int PIN_LED_ROJO = 26;     // LED indicador de alerta
const int PIN_LED_VERDE = 27;    // LED indicador de estado normal
const int PIN_LED_AZUL = 14;     // LED indicador de actividad

// ========================================
// VARIABLES GLOBALES
// ========================================
unsigned long ultimaLectura = 0;
const unsigned long intervaloLectura = 10000; // Leer cada 10 segundos

bool ventiladorActivo = false;
int valorCO2 = 0;

// ========================================
// SETUP
// ========================================
void setup() {
Serial.begin(115200);
delay(1000);

Serial.println("\n=================================");
Serial.println("ESP32 - Salud Ocupacional");
Serial.println("=================================\n");

// Configurar pines
pinMode(PIN_RELE_VENTILADOR, OUTPUT);
pinMode(PIN_LED_ROJO, OUTPUT);
pinMode(PIN_LED_VERDE, OUTPUT);
pinMode(PIN_LED_AZUL, OUTPUT);

// Estado inicial
digitalWrite(PIN_RELE_VENTILADOR, LOW);
digitalWrite(PIN_LED_ROJO, LOW);
digitalWrite(PIN_LED_VERDE, HIGH); // Verde encendido = sistema OK
digitalWrite(PIN_LED_AZUL, LOW);

// Conectar a WiFi
conectarWiFi();

// Registrar dispositivo en API
registrarDispositivo();

Serial.println("\n✓ Sistema iniciado correctamente");
}

// ========================================
// LOOP PRINCIPAL
// ========================================
void loop() {
unsigned long tiempoActual = millis();

// Verificar conexión WiFi
if (WiFi.status() != WL_CONNECTED) {
Serial.println("⚠️ WiFi desconectado, reconectando...");
conectarWiFi();
}

// Leer sensores y enviar datos cada intervalo
if (tiempoActual - ultimaLectura >= intervaloLectura) {
ultimaLectura = tiempoActual;

// Parpadeo LED azul (actividad)
digitalWrite(PIN_LED_AZUL, HIGH);

// Leer sensor MQ135
valorCO2 = leerSensorCO2();

// Enviar lectura a API
enviarLecturaSensor(valorCO2);

// Consultar comandos pendientes
verificarComandos();

digitalWrite(PIN_LED_AZUL, LOW);
}

delay(100);
}

// ========================================
// FUNCIONES DE RED
// ========================================

void conectarWiFi() {
Serial.print("Conectando a WiFi");
WiFi.begin(ssid, password);

int intentos = 0;
while (WiFi.status() != WL_CONNECTED && intentos < 30) {
delay(500);
Serial.print(".");
intentos++;
}

if (WiFi.status() == WL_CONNECTED) {
Serial.println("\n✓ WiFi conectado");
Serial.print("IP: ");
Serial.println(WiFi.localIP());
} else {
Serial.println("\n❌ Error conectando WiFi");
}
}

void registrarDispositivo() {
if (WiFi.status() != WL_CONNECTED) return;

HTTPClient http;
String endpoint = String(apiURL) + "/api/esp32/registrar";

http.begin(endpoint);
http.addHeader("Content-Type", "application/json");

StaticJsonDocument<200> doc;
doc["device_id"] = deviceID;
doc["tipo"] = "sensor_actuador";
doc["sensores"] = "MQ135";
doc["actuadores"] = "ventilador,leds";

String jsonString;
serializeJson(doc, jsonString);

int httpCode = http.POST(jsonString);

if (httpCode > 0) {
String response = http.getString();
Serial.println("✓ Dispositivo registrado en API");
Serial.println("Respuesta: " + response);
} else {
Serial.println("❌ Error registrando dispositivo");
}

http.end();
}

void enviarLecturaSensor(int co2) {
if (WiFi.status() != WL_CONNECTED) return;

HTTPClient http;
String endpoint = String(apiURL) + "/api/esp32/lectura";

http.begin(endpoint);
http.addHeader("Content-Type", "application/json");

StaticJsonDocument<300> doc;
doc["device_id"] = deviceID;
doc["tipo_sensor"] = "co2";
doc["valor"] = co2;
doc["unidad"] = "ppm";
doc["timestamp"] = millis();

String jsonString;
serializeJson(doc, jsonString);

int httpCode = http.POST(jsonString);

if (httpCode > 0) {
Serial.print("📤 Lectura enviada - CO2: ");
Serial.print(co2);
Serial.println(" ppm");
} else {
Serial.println("❌ Error enviando lectura");
}

http.end();
}

void verificarComandos() {
if (WiFi.status() != WL_CONNECTED) return;

HTTPClient http;
String endpoint = String(apiURL) + "/api/esp32/comandos?device_id=" + deviceID;

http.begin(endpoint);
int httpCode = http.GET();

if (httpCode == 200) {
String payload = http.getString();

StaticJsonDocument<512> doc;
DeserializationError error = deserializeJson(doc, payload);

if (!error && doc["success"] == true) {
    JsonArray comandos = doc["comandos"].as<JsonArray>();
    
    for (JsonObject comando : comandos) {
    String accion = comando["accion"].as<String>();
    String parametro = comando["parametro"].as<String>();
    int comandoId = comando["id"];
    
    Serial.print("📥 Comando recibido: ");
    Serial.println(accion);
    
    ejecutarComando(accion, parametro);
    confirmarComando(comandoId);
    }
}
}

http.end();
}

void confirmarComando(int comandoId) {
if (WiFi.status() != WL_CONNECTED) return;

HTTPClient http;
String endpoint = String(apiURL) + "/api/esp32/comando/confirmar";

http.begin(endpoint);
http.addHeader("Content-Type", "application/json");

StaticJsonDocument<200> doc;
doc["comando_id"] = comandoId;
doc["device_id"] = deviceID;
doc["estado"] = "ejecutado";

String jsonString;
serializeJson(doc, jsonString);

http.POST(jsonString);
http.end();
}

// ========================================
// FUNCIONES DE SENSORES
// ========================================

int leerSensorCO2() {
// Leer valor analógico del MQ135
int valorAnalogico = analogRead(PIN_MQ135);

// Convertir a PPM (calibración aproximada)
// Nota: Requiere calibración específica del sensor
int ppm = map(valorAnalogico, 0, 4095, 400, 2000);

// Limitar valores
ppm = constrain(ppm, 400, 5000);

return ppm;
}

// ========================================
// FUNCIONES DE ACTUADORES
// ========================================

void ejecutarComando(String accion, String parametro) {
if (accion == "activar_ventilador") {
activarVentilador(true);
} 
else if (accion == "desactivar_ventilador") {
activarVentilador(false);
}
else if (accion == "led_alerta") {
if (parametro == "rojo") {
    digitalWrite(PIN_LED_ROJO, HIGH);
    digitalWrite(PIN_LED_VERDE, LOW);
} else if (parametro == "verde") {
    digitalWrite(PIN_LED_VERDE, HIGH);
    digitalWrite(PIN_LED_ROJO, LOW);
}
}
else if (accion == "leds_off") {
digitalWrite(PIN_LED_ROJO, LOW);
digitalWrite(PIN_LED_VERDE, LOW);
}
}

void activarVentilador(bool estado) {
ventiladorActivo = estado;
digitalWrite(PIN_RELE_VENTILADOR, estado ? HIGH : LOW);

Serial.print("🌀 Ventilador: ");
Serial.println(estado ? "ACTIVADO" : "DESACTIVADO");
}