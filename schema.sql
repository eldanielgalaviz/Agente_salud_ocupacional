-- ========================================
-- BASE DE DATOS: SALUD OCUPACIONAL
-- Versión Simplificada (Sin Arduino)
-- ========================================

CREATE DATABASE IF NOT EXISTS salud_ocupacional;
USE salud_ocupacional;

-- ========================================
-- TABLA DE USUARIOS
-- ========================================
CREATE TABLE usuarios (
    id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========================================
-- TABLA DE SESIONES DE TRABAJO
-- ========================================
CREATE TABLE sesiones_trabajo (
    id INT PRIMARY KEY AUTO_INCREMENT,
    usuario_id INT NOT NULL,
    fecha DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME,
    minutos_totales INT DEFAULT 0,
    pausas_tomadas INT DEFAULT 0,
    estado ENUM('activa', 'pausada', 'finalizada') DEFAULT 'activa',
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id) ON DELETE CASCADE
);

-- ========================================
-- TABLA DE LECTURAS DE SENSORES (SIMULADAS)
-- ========================================
CREATE TABLE lecturas_sensores (
    id INT PRIMARY KEY AUTO_INCREMENT,
    sesion_id INT NOT NULL,
    tipo_sensor ENUM('co2', 'ruido', 'temperatura') NOT NULL,
    valor DECIMAL(10, 2) NOT NULL,
    unidad VARCHAR(10),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sesion_id) REFERENCES sesiones_trabajo(id) ON DELETE CASCADE,
    INDEX idx_sesion_sensor (sesion_id, tipo_sensor),
    INDEX idx_timestamp (timestamp)
);

-- ========================================
-- TABLA DE DETECCIÓN DE FATIGA
-- ========================================
CREATE TABLE deteccion_fatiga (
    id INT PRIMARY KEY AUTO_INCREMENT,
    sesion_id INT NOT NULL,
    tipo_fatiga ENUM('visual', 'postural', 'cognitiva') NOT NULL,
    nivel_fatiga ENUM('bajo', 'moderado', 'alto') NOT NULL,
    indicador VARCHAR(100),
    frecuencia_parpadeo INT,
    postura_detectada VARCHAR(50),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sesion_id) REFERENCES sesiones_trabajo(id) ON DELETE CASCADE,
    INDEX idx_sesion_tipo (sesion_id, tipo_fatiga)
);

-- ========================================
-- TABLA DE ALERTAS GENERADAS
-- ========================================
CREATE TABLE alertas_generadas (
    id INT PRIMARY KEY AUTO_INCREMENT,
    sesion_id INT NOT NULL,
    tipo_alerta VARCHAR(50) NOT NULL,
    prioridad ENUM('alta', 'media', 'baja') NOT NULL,
    mensaje TEXT NOT NULL,
    visualizada BOOLEAN DEFAULT FALSE,
    descartada BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sesion_id) REFERENCIAS sesiones_trabajo(id) ON DELETE CASCADE,
    INDEX idx_sesion_prioridad (sesion_id, prioridad)
);

-- ========================================
-- TABLA DE ACCIONES DEL SISTEMA
-- ========================================
CREATE TABLE acciones_sistema (
    id INT PRIMARY KEY AUTO_INCREMENT,
    sesion_id INT NOT NULL,
    tipo_accion VARCHAR(50) NOT NULL,
    descripcion TEXT,
    automatica BOOLEAN DEFAULT TRUE,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sesion_id) REFERENCES sesiones_trabajo(id) ON DELETE CASCADE
);

-- ========================================
-- TABLA DE DISPOSITIVOS ESP32
-- ========================================
CREATE TABLE IF NOT EXISTS dispositivos_esp32 (
    id INT PRIMARY KEY AUTO_INCREMENT,
    device_id VARCHAR(50) UNIQUE NOT NULL,
    tipo VARCHAR(50) NOT NULL,
    sensores TEXT,
    actuadores TEXT,
    estado ENUM('activo', 'inactivo', 'error') DEFAULT 'activo',
    ultima_conexion TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ========================================
-- TABLA DE COMANDOS PARA ESP32
-- ========================================
CREATE TABLE IF NOT EXISTS comandos_esp32 (
    id INT PRIMARY KEY AUTO_INCREMENT,
    device_id VARCHAR(50) NOT NULL,
    accion VARCHAR(50) NOT NULL,
    parametro VARCHAR(100),
    estado ENUM('pendiente', 'ejecutado', 'error') DEFAULT 'pendiente',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ejecutado_at TIMESTAMP NULL,
    FOREIGN KEY (device_id) REFERENCES dispositivos_esp32(device_id) ON DELETE CASCADE,
    INDEX idx_device_estado (device_id, estado)
);

-- Insertar dispositivo de ejemplo
INSERT INTO dispositivos_esp32 (device_id, tipo, sensores, actuadores) VALUES
('ESP32_ESCRITORIO_01', 'sensor_actuador', 'MQ135', 'ventilador,leds');
-- ========================================
-- DATOS DE EJEMPLO
-- ========================================

-- Usuario de prueba
INSERT INTO usuarios (nombre, apellido, email) VALUES
('Usuario', 'Demo', 'demo@ejemplo.com');

-- Sesión activa de prueba
INSERT INTO sesiones_trabajo (usuario_id, fecha, hora_inicio, estado) VALUES
(1, CURDATE(), CURTIME(), 'activa');

-- Lecturas iniciales simuladas
INSERT INTO lecturas_sensores (sesion_id, tipo_sensor, valor, unidad) VALUES
(1, 'co2', 450, 'ppm'),
(1, 'ruido', 45, 'dB'),
(1, 'temperatura', 23, '°C');

-- ========================================
-- VISTAS ÚTILES
-- ========================================

CREATE VIEW vista_sesion_actual AS
SELECT 
    s.id AS sesion_id,
    s.usuario_id,
    u.nombre,
    u.apellido,
    s.fecha,
    s.hora_inicio,
    s.minutos_totales,
    s.estado,
    (SELECT valor FROM lecturas_sensores WHERE sesion_id = s.id AND tipo_sensor = 'co2' ORDER BY timestamp DESC LIMIT 1) AS ultimo_co2,
    (SELECT valor FROM lecturas_sensores WHERE sesion_id = s.id AND tipo_sensor = 'ruido' ORDER BY timestamp DESC LIMIT 1) AS ultimo_ruido,
    (SELECT valor FROM lecturas_sensores WHERE sesion_id = s.id AND tipo_sensor = 'temperatura' ORDER BY timestamp DESC LIMIT 1) AS ultima_temperatura
FROM sesiones_trabajo s
JOIN usuarios u ON s.usuario_id = u.id
WHERE s.estado = 'activa';

-- ========================================
-- FIN DEL ESQUEMA
-- ========================================