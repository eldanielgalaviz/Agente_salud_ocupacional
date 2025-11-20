import React, { useState, useEffect } from 'react';
import { Activity, Wind, Volume2, Eye, AlertCircle, CheckCircle } from 'lucide-react';

const API_URL = 'http://localhost:3001';

const DashboardSaludOcupacional = () => {
  // Estados para datos en tiempo real
  const [datosSensores, setDatosSensores] = useState({
    co2: 450,
    ruido: 45,
    temperatura: 23
  });

  const [estadoFatiga, setEstadoFatiga] = useState({
    visual: 'bajo',
    postural: 'bajo',
    cognitiva: 'bajo'
  });

  const [alertasActivas, setAlertasActivas] = useState([]);
  
  const [estadoActuadores, setEstadoActuadores] = useState({
    ventilador: 'apagado',
    ledVerde: false,
    ledAmarillo: false,
    ledRojo: false
  });

  const [sesionActual, setSesionActual] = useState({
    activa: true,
    minutosTranscurridos: 0,
    pausasTomadas: 0
  });

  const [dispositivos, setDispositivos] = useState([]);
  const [error, setError] = useState(null);

  // Obtener datos del backend cada 5 segundos
  useEffect(() => {
    const fetchDatos = async () => {
      try {
        const response = await fetch(`${API_URL}/api/dashboard/datos-completos`);
        const resultado = await response.json();

        if (resultado.success) {
          const { data } = resultado;
          
          setDatosSensores(data.datosSensores);
          setEstadoFatiga(data.estadoFatiga);
          setAlertasActivas(data.alertasActivas);
          setEstadoActuadores(data.estadoActuadores);
          setSesionActual(data.sesionActual);
          setDispositivos(data.dispositivos);
          setError(null);
        } else {
          // Si hay error pero devuelve datos por defecto
          if (resultado.data) {
            setDatosSensores(resultado.data.datosSensores);
            setEstadoFatiga(resultado.data.estadoFatiga);
            setAlertasActivas(resultado.data.alertasActivas || []);
            setEstadoActuadores(resultado.data.estadoActuadores);
            setSesionActual(resultado.data.sesionActual);
          }
          setError('Usando datos por defecto');
        }
      } catch (err) {
        console.error('Error al obtener datos:', err);
        setError('No se pudo conectar con el servidor');
      }
    };

    // Llamada inicial
    fetchDatos();

    // Actualizar cada 5 segundos
    const intervalo = setInterval(fetchDatos, 5000);

    return () => clearInterval(intervalo);
  }, []);

  // Función para determinar color según nivel
  const getColorCO2 = (valor) => {
    if (valor < 800) return 'text-green-500';
    if (valor < 1000) return 'text-yellow-500';
    if (valor < 1500) return 'text-orange-500';
    return 'text-red-500';
  };

  const getColorRuido = (valor) => {
    if (valor < 50) return 'text-green-500';
    if (valor < 65) return 'text-yellow-500';
    return 'text-red-500';
  };

  const getColorFatiga = (nivel) => {
    if (nivel === 'bajo') return 'text-green-500';
    if (nivel === 'moderado') return 'text-yellow-500';
    return 'text-red-500';
  };

  const getPrioridadColor = (prioridad) => {
    if (prioridad === 'alta') return 'bg-red-50 border-red-500 text-red-800';
    if (prioridad === 'media') return 'bg-yellow-50 border-yellow-500 text-yellow-800';
    return 'bg-blue-50 border-blue-500 text-blue-800';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold text-gray-800 mb-2">
              🏥 Agente Inteligente - Salud Ocupacional
            </h1>
            <p className="text-gray-600">Sistema de monitoreo y optimización de ambiente laboral</p>
          </div>
          <div className="text-right">
            {error && (
              <p className="text-red-500 text-sm mb-2">⚠️ {error}</p>
            )}
            {dispositivos.length > 0 && (
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${
                  dispositivos[0].conectado ? 'bg-green-500 animate-pulse' : 'bg-red-500'
                }`}></div>
                <span className="text-sm text-gray-600">
                  {dispositivos[0].conectado ? 'ESP32 Conectado' : 'ESP32 Desconectado'}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Sesión Actual */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <h2 className="text-xl font-bold text-gray-800 mb-4">📊 Sesión Actual</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-blue-50 rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-1">Estado</p>
            <p className="text-2xl font-bold text-blue-600">
              {sesionActual.activa ? 'Activa' : 'Finalizada'}
            </p>
          </div>
          <div className="bg-purple-50 rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-1">Tiempo Trabajado</p>
            <p className="text-2xl font-bold text-purple-600">
              {sesionActual.minutosTranscurridos} min
            </p>
          </div>
          <div className="bg-green-50 rounded-lg p-4">
            <p className="text-sm text-gray-600 mb-1">Pausas Tomadas</p>
            <p className="text-2xl font-bold text-green-600">
              {sesionActual.pausasTomadas}
            </p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Panel de Sensores */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
            <Activity className="mr-2" /> Lecturas de Sensores
          </h2>
          
          {/* CO2 */}
          <div className="mb-4 p-4 bg-gray-50 rounded-lg">
            <div className="flex justify-between items-center mb-2">
              <span className="font-semibold text-gray-700">CO₂</span>
              <span className={`text-2xl font-bold ${getColorCO2(datosSensores.co2)}`}>
                {Math.round(datosSensores.co2)} ppm
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div 
                className={`h-3 rounded-full transition-all ${
                  datosSensores.co2 < 800 ? 'bg-green-500' :
                  datosSensores.co2 < 1000 ? 'bg-yellow-500' :
                  datosSensores.co2 < 1500 ? 'bg-orange-500' : 'bg-red-500'
                }`}
                style={{ width: `${Math.min((datosSensores.co2 / 2000) * 100, 100)}%` }}
              ></div>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Óptimo: &lt;800 | Aceptable: 800-1000 | Crítico: &gt;1200
            </p>
          </div>

          {/* Ruido */}
          <div className="mb-4 p-4 bg-gray-50 rounded-lg">
            <div className="flex justify-between items-center mb-2">
              <span className="font-semibold text-gray-700 flex items-center">
                <Volume2 className="mr-2 w-5 h-5" /> Ruido
              </span>
              <span className={`text-2xl font-bold ${getColorRuido(datosSensores.ruido)}`}>
                {Math.round(datosSensores.ruido)} dB
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div 
                className={`h-3 rounded-full transition-all ${
                  datosSensores.ruido < 50 ? 'bg-green-500' :
                  datosSensores.ruido < 65 ? 'bg-yellow-500' : 'bg-red-500'
                }`}
                style={{ width: `${(datosSensores.ruido / 100) * 100}%` }}
              ></div>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Tranquilo: &lt;50 | Moderado: 50-65 | Ruidoso: &gt;65
            </p>
          </div>

          {/* Temperatura */}
          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="flex justify-between items-center mb-2">
              <span className="font-semibold text-gray-700">🌡️ Temperatura</span>
              <span className="text-2xl font-bold text-blue-600">
                {datosSensores.temperatura.toFixed(1)}°C
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-3">
              <div 
                className="bg-blue-500 h-3 rounded-full transition-all"
                style={{ width: `${Math.min(Math.max(((datosSensores.temperatura - 15) / 15) * 100, 0), 100)}%` }}
              ></div>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Óptimo: 22-24°C
            </p>
          </div>
        </div>

        {/* Panel de Detección de Fatiga */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
            <Eye className="mr-2" /> Detección de Fatiga
          </h2>

          {/* Fatiga Visual */}
          <div className="mb-4 p-4 bg-gray-50 rounded-lg">
            <div className="flex justify-between items-center">
              <div>
                <p className="font-semibold text-gray-700">Fatiga Visual</p>
                <p className="text-xs text-gray-500">Análisis de parpadeo y mirada</p>
              </div>
              <div className="text-right">
                <span className={`text-xl font-bold uppercase ${getColorFatiga(estadoFatiga.visual)}`}>
                  {estadoFatiga.visual}
                </span>
              </div>
            </div>
          </div>

          {/* Fatiga Postural */}
          <div className="mb-4 p-4 bg-gray-50 rounded-lg">
            <div className="flex justify-between items-center">
              <div>
                <p className="font-semibold text-gray-700">Fatiga Postural</p>
                <p className="text-xs text-gray-500">Análisis de posición</p>
              </div>
              <div className="text-right">
                <span className={`text-xl font-bold uppercase ${getColorFatiga(estadoFatiga.postural)}`}>
                  {estadoFatiga.postural}
                </span>
              </div>
            </div>
          </div>

          {/* Fatiga Cognitiva */}
          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="flex justify-between items-center">
              <div>
                <p className="font-semibold text-gray-700">Fatiga Cognitiva</p>
                <p className="text-xs text-gray-500">Tiempo de trabajo continuo</p>
              </div>
              <div className="text-right">
                <span className={`text-xl font-bold uppercase ${getColorFatiga(estadoFatiga.cognitiva)}`}>
                  {estadoFatiga.cognitiva}
                </span>
              </div>
            </div>
          </div>

          {/* Recomendación */}
          <div className="mt-4 p-4 bg-blue-50 rounded-lg border-l-4 border-blue-500">
            <p className="text-sm font-semibold text-blue-800 mb-1">💡 Recomendación</p>
            <p className="text-sm text-blue-700">
              {sesionActual.minutosTranscurridos > 50 
                ? "Es momento de tomar una pausa de 5 minutos"
                : "Todo va bien. Mantén tu postura correcta"}
            </p>
          </div>
        </div>
      </div>

      {/* Alertas Activas */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
          <AlertCircle className="mr-2" /> Alertas Activas
        </h2>
        
        {alertasActivas.length > 0 ? (
          <div className="space-y-3">
            {alertasActivas.map((alerta) => (
              <div 
                key={alerta.id}
                className={`flex items-start p-4 border-l-4 rounded ${getPrioridadColor(alerta.prioridad)}`}
              >
                <AlertCircle className="mr-3 mt-1 flex-shrink-0" />
                <div>
                  <p className="font-semibold">{alerta.tipo_alerta}</p>
                  <p className="text-sm">{alerta.mensaje}</p>
                  <p className="text-xs mt-1 opacity-75">
                    {new Date(alerta.timestamp).toLocaleTimeString('es-MX')}
                  </p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="flex items-center p-4 bg-green-50 border-l-4 border-green-500 rounded">
            <CheckCircle className="text-green-500 mr-3" />
            <p className="text-green-700 font-medium">
              No hay alertas activas. Condiciones de trabajo óptimas.
            </p>
          </div>
        )}
      </div>

      {/* Estado de Actuadores */}
      <div className="bg-white rounded-lg shadow-lg p-6">
        <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
          <Wind className="mr-2" /> Estado de Actuadores
        </h2>
        
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {/* Ventilador */}
          <div className="p-4 bg-gray-50 rounded-lg text-center">
            <Wind className={`mx-auto mb-2 ${estadoActuadores.ventilador === 'encendido' ? 'text-blue-500' : 'text-gray-400'}`} size={32} />
            <p className="font-semibold text-gray-700">Ventilador</p>
            <p className={`text-sm ${estadoActuadores.ventilador === 'encendido' ? 'text-blue-600' : 'text-gray-500'}`}>
              {estadoActuadores.ventilador.toUpperCase()}
            </p>
          </div>

          {/* LED Verde */}
          <div className="p-4 bg-gray-50 rounded-lg text-center">
            <div className={`w-8 h-8 rounded-full mx-auto mb-2 ${
              estadoActuadores.ledVerde
                ? 'bg-green-500 shadow-lg shadow-green-300' 
                : 'bg-gray-300'
            }`}></div>
            <p className="font-semibold text-gray-700">LED Verde</p>
            <p className="text-sm text-gray-500">Estado OK</p>
          </div>

          {/* LED Amarillo */}
          <div className="p-4 bg-gray-50 rounded-lg text-center">
            <div className={`w-8 h-8 rounded-full mx-auto mb-2 ${
              estadoActuadores.ledAmarillo
                ? 'bg-yellow-500 shadow-lg shadow-yellow-300' 
                : 'bg-gray-300'
            }`}></div>
            <p className="font-semibold text-gray-700">LED Amarillo</p>
            <p className="text-sm text-gray-500">Precaución</p>
          </div>

          {/* LED Rojo */}
          <div className="p-4 bg-gray-50 rounded-lg text-center">
            <div className={`w-8 h-8 rounded-full mx-auto mb-2 ${
              estadoActuadores.ledRojo
                ? 'bg-red-500 shadow-lg shadow-red-300 animate-pulse' 
                : 'bg-gray-300'
            }`}></div>
            <p className="font-semibold text-gray-700">LED Rojo</p>
            <p className="text-sm text-gray-500">Alerta</p>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="mt-6 text-center text-gray-600 text-sm">
        <p>🤖 Sistema de Agente Inteligente | Universidad Autónoma de Sinaloa</p>
        <p className="mt-1">Actualización en tiempo real cada 5 segundos</p>
      </div>
    </div>
  );
};

export default DashboardSaludOcupacional;