% BASE DE CONOCIMIENTO - SALUD OCUPACIONAL


% HECHOS ESTÁTICOS (Estándares y Umbrales)

% Estándares de calidad del aire (CO2 en ppm)
estandar_co2(optimo, 400, 800).
estandar_co2(aceptable, 801, 1000).
estandar_co2(deficiente, 1001, 1500).
estandar_co2(malo, 1501, 5000).

% Estándares de nivel de ruido (dB)
estandar_ruido(silencioso, 0, 40).
estandar_ruido(tranquilo, 41, 50).
estandar_ruido(moderado, 51, 65).
estandar_ruido(ruidoso, 66, 85).
estandar_ruido(muy_ruidoso, 86, 120).

% Estándares de temperatura ambiente (°C)
estandar_temperatura(frio, 0, 18).
estandar_temperatura(fresco, 19, 21).
estandar_temperatura(optimo, 22, 24).
estandar_temperatura(calido, 25, 27).
estandar_temperatura(caluroso, 28, 40).

% Indicadores de fatiga visual
indicador_fatiga(parpadeo_frecuente, visual, moderado).
indicador_fatiga(ojos_entrecerrados, visual, alto).
indicador_fatiga(frotarse_ojos, visual, alto).
indicador_fatiga(mirada_perdida, cognitiva, moderado).
    
% Indicadores de fatiga postural
indicador_fatiga(cabeza_inclinada, postural, moderado).
indicador_fatiga(hombros_caidos, postural, alto).
indicador_fatiga(espalda_encorvada, postural, alto).
indicador_fatiga(cuello_extendido, postural, moderado).

% Tiempos recomendados (minutos)
tiempo_trabajo_continuo(50).
tiempo_pausa_corta(5).
tiempo_pausa_larga(15).
intervalo_ejercicios(30).

% Ejercicios recomendados por tipo de fatiga
ejercicio(visual, '20-20-20: cada 20 min, mirar 20 seg a 20 pies', 1).
ejercicio(postural, 'Estiramiento de cuello: 10 repeticiones', 2).
ejercicio(postural, 'Rotacion de hombros: 15 repeticiones', 2).
ejercicio(postural, 'Estiramiento de espalda: mantener 30 seg', 3).
ejercicio(cognitiva, 'Respiracion profunda: 5 repeticiones', 2).
ejercicio(general, 'Caminar 5 minutos', 5).
ejercicio(general, 'Estiramiento completo de brazos', 1).

% Umbrales personalizables por usuario
umbral_default(co2_critico, 1200).
umbral_default(ruido_critico, 70).
umbral_default(tiempo_max_sentado, 60).
umbral_default(frecuencia_parpadeo_normal, 15).
umbral_default(frecuencia_parpadeo_fatiga, 25).

% Acciones correctivas
accion_correctiva(co2_alto, activar_ventilador, automatica).
accion_correctiva(co2_alto, sugerir_ventilar, manual).
accion_correctiva(ruido_alto, alerta_ruido, manual).
accion_correctiva(fatiga_visual, ejercicio_visual, manual).
accion_correctiva(fatiga_postural, ejercicio_postural, manual).
accion_correctiva(tiempo_prolongado, sugerir_pausa, manual).

% Prioridades de alertas (1=alta, 2=media, 3=baja)
prioridad_alerta(co2_critico, 1).
prioridad_alerta(fatiga_alta, 1).
prioridad_alerta(ruido_excesivo, 2).
prioridad_alerta(tiempo_trabajo_largo, 2).
prioridad_alerta(postura_inadecuada, 3).

% Mensajes para el usuario
mensaje_alerta(co2_alto, 'Nivel de CO2 elevado. Activando ventilador.').
mensaje_alerta(ruido_alto, 'Nivel de ruido elevado. Considera usar audifonos.').
mensaje_alerta(fatiga_detectada, 'Signos de fatiga detectados. Toma un descanso.').
mensaje_alerta(pausa_recomendada, 'Llevas mucho tiempo trabajando. Pausa recomendada.').
mensaje_alerta(ejercicio_sugerido, 'Es momento de hacer ejercicios de estiramiento.').


% HECHOS DINÁMICOS (Estado actual del sistema)
% Estos se actualizarán desde Python/MySQL

:- dynamic(estado_actual/2).
:- dynamic(sesion_trabajo/3).
:- dynamic(lectura_sensor/3).
:- dynamic(nivel_fatiga/2).
:- dynamic(usuario_actual/1).
:- dynamic(preferencia_usuario/3).

% Estados iniciales por defecto
estado_actual(ventilador, apagado).
estado_actual(alerta_activa, ninguna).

% Sesión de trabajo: sesion_trabajo(ID, HoraInicio, MinutosTranscurridos)
sesion_trabajo(1, '09:00:00', 0).

% Lecturas de sensores: lectura_sensor(TipoSensor, Valor, Timestamp)
lectura_sensor(co2, 450, '09:00:00').
lectura_sensor(ruido, 45, '09:00:00').
lectura_sensor(temperatura, 23, '09:00:00').

% Nivel de fatiga: nivel_fatiga(TipoFatiga, Nivel)
nivel_fatiga(visual, bajo).
nivel_fatiga(postural, bajo).
nivel_fatiga(cognitiva, bajo).

% Usuario actual
usuario_actual(default).

% Preferencias por usuario: preferencia_usuario(Usuario, Parametro, Valor)
preferencia_usuario(default, sensibilidad_alertas, media).
preferencia_usuario(default, volumen_alertas, 70).
preferencia_usuario(default, frecuencia_recordatorios, 60).


% REGLAS DE INFERENCIA (Mínimo 8 reglas)

% REGLA 1: Evaluación de calidad del aire
calidad_aire(Nivel) :-
    lectura_sensor(co2, CO2, _),
    estandar_co2(Nivel, Min, Max),
    CO2 >= Min,
    CO2 =< Max.

% REGLA 2: Evaluación de nivel de ruido
nivel_ruido(Nivel) :-
    lectura_sensor(ruido, Ruido, _),
    estandar_ruido(Nivel, Min, Max),
    Ruido >= Min,
    Ruido =< Max.

% REGLA 3: Detección de condición crítica de CO2
condicion_critica_co2 :-
    lectura_sensor(co2, CO2, _),
    umbral_default(co2_critico, Umbral),
    CO2 >= Umbral.

% REGLA 4: Necesidad de activar ventilador
requiere_ventilacion :-
    condicion_critica_co2,
    estado_actual(ventilador, apagado).

% REGLA 5: Detección de fatiga general alta
fatiga_general_alta :-
    (nivel_fatiga(visual, alto) ; 
    nivel_fatiga(postural, alto) ; 
    nivel_fatiga(cognitiva, alto)).

% REGLA 6: Necesidad de pausa por tiempo prolongado
requiere_pausa :-
    sesion_trabajo(_, _, Minutos),
    tiempo_trabajo_continuo(MaxTiempo),
    Minutos >= MaxTiempo.

% REGLA 7: Recomendación de ejercicio específico
recomendar_ejercicio(Tipo, Descripcion) :-
    nivel_fatiga(Tipo, Nivel),
    (Nivel = alto ; Nivel = moderado),
    ejercicio(Tipo, Descripcion, _).

% REGLA 8: Condición de ambiente laboral óptimo
ambiente_optimo :-
    calidad_aire(optimo),
    nivel_ruido(Nivel),
    (Nivel = silencioso ; Nivel = tranquilo),
    \+ fatiga_general_alta.

% REGLA 9: Priorizar acción correctiva
accion_prioritaria(Accion) :-
    condicion_critica_co2,
    accion_correctiva(co2_alto, Accion, _),
    prioridad_alerta(co2_critico, 1).

% REGLA 10: Verificar necesidad de multiples intervenciones
necesita_intervencion_multiple :-
    condicion_critica_co2,
    fatiga_general_alta,
    requiere_pausa.


% REGLAS DE CONSULTA ÚTILES


% Obtener todas las acciones recomendadas actualmente
acciones_recomendadas(Lista) :-
    findall(Accion, (
        (condicion_critica_co2, accion_correctiva(co2_alto, Accion, _)) ;
        (fatiga_general_alta, accion_correctiva(fatiga_visual, Accion, _)) ;
        (requiere_pausa, accion_correctiva(tiempo_prolongado, Accion, _))
    ), Lista).

% Obtener estado completo del sistema
estado_sistema(Estado) :-
    calidad_aire(CalidadAire),
    nivel_ruido(NivelRuido),
    estado_actual(ventilador, EstadoVentilador),
    sesion_trabajo(_, _, MinutosTrabajo),
    Estado = [
        calidad_aire(CalidadAire),
        ruido(NivelRuido),
        ventilador(EstadoVentilador),
        minutos_trabajo(MinutosTrabajo)
    ].

% Verificar si el sistema está en estado de alerta
sistema_en_alerta :-
    (condicion_critica_co2 ; fatiga_general_alta ; requiere_pausa).


% PREDICADOS AUXILIARES PARA ACTUALIZACIÓN


% Actualizar lectura de sensor
actualizar_sensor(Tipo, Valor, Timestamp) :-
    retractall(lectura_sensor(Tipo, _, _)),
    assertz(lectura_sensor(Tipo, Valor, Timestamp)).

% Actualizar nivel de fatiga
actualizar_fatiga(Tipo, Nivel) :-
    retractall(nivel_fatiga(Tipo, _)),
    assertz(nivel_fatiga(Tipo, Nivel)).

% Actualizar estado de actuador
actualizar_actuador(Actuador, Estado) :-
    retractall(estado_actual(Actuador, _)),
    assertz(estado_actual(Actuador, Estado)).

% Actualizar tiempo de sesión
actualizar_sesion(ID, Minutos) :-
    retractall(sesion_trabajo(ID, _, _)),
    sesion_trabajo(ID, Hora, _),
    assertz(sesion_trabajo(ID, Hora, Minutos)).