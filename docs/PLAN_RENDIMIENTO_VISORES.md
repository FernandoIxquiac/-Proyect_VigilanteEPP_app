# Plan incremental de rendimiento de los tres visores

Fecha: 21 de octubre de 2026.
Estado: historico. El visor web y el monitor web se retiraron tras las
regresiones observadas; el video en vivo usa exclusivamente la ventana nativa.
Este plan no debe ejecutarse de nuevo sin una nueva decision de arquitectura.

## Objetivo y alcance

Mejorar el arranque y la respuesta del visor de la pagina principal, la ventana
flotante de OpenCV y el monitor web `?view=monitor`. Conservar una sola captura,
un solo detector activo y la persistencia existente.

Referencia: `PROJECT_MAP.md`. El plan historico `PLAN.md` contiene otros cambios
de interfaz; no forma parte de este encargo. La demostracion con camara, cambios
de diseño, migraciones de datos y nuevas dependencias quedan fuera del alcance.

## Instrucciones comunes para el modelo ejecutor

- Ejecutar un solo bloque por encargo. Entregar su resultado y detenerse; no
  implementar los bloques siguientes por iniciativa propia.
- Leer AGENTS.md, este documento y solo las funciones relacionadas en el mapa.
  No repetir una auditoria completa del repositorio ni crear otros agentes.
- Usar el entorno con el que arranca actualmente el programa. No reinstalar
  paquetes, crear entornos, cambiar versiones, pesos, instaladores ni modelos
  de agentes. No utilizar el entorno retirado dentro de `data/recovery/`.
- Preservar todos los cambios previos, incluidos los archivos sin seguimiento
  de Git. En particular, `modules/auditor.py` ya existia antes de este plan.
- Antes de editar, guardar una copia de los archivos exactos que se modificaran
  en una carpeta nueva de `data/recovery/`. Registrar archivos nuevos por separado.
  No copiar entornos, dependencias ni datasets para este respaldo de codigo.
- Seguir las reglas del proyecto: sin emojis, excepciones especificas y logica
  reutilizable en `modules/`, conservando comentarios y docstrings existentes.
- Las pruebas automaticas deben usar camaras simuladas, imagenes en memoria y
  almacenamiento temporal. No inicializar ni escribir en la base operativa al
  importar modulos para probarlos; aislar o sustituir esas dependencias primero.
- No presentar una prueba con camara simulada como validacion del hardware real.
- Si aparece un fallo, corregirlo dentro del bloque y repetir la prueba afectada.
  Si requiere ampliar el alcance, describir el bloqueo y dejar un cambio revisable.
- No hacer commit, publicar ni activar procesos permanentes como parte del encargo.

## Flujo actual confirmado

`ThreadedCamera` ya captura en un hilo y conserva la ultima imagen.
`LiveAuditorService._audit_loop` lee esa imagen y ejecuta, en secuencia:

1. Inferencia y tracking en `detect_objects`.
2. Evaluacion y dibujo de resultados.
3. Registro de eventos y escritura de evidencias, cuando corresponde.
4. Compresion JPEG, actualizacion de la ventana nativa y publicacion del estado.

Los dos visores web leen ese estado cada 0,10 segundos. Ese intervalo no asegura
que existan diez imagenes nuevas por segundo. La ventana nativa procesa sus
eventos despues de las operaciones anteriores, por lo que tambien espera a YOLO.

Puntos de entrada:

| Archivo | Funciones o secciones relevantes |
| --- | --- |
| `modules/camera.py` | `ThreadedCamera.start`, `_reader_loop`, `read`, `stop` |
| `modules/auditor.py` | `start`, `stop`, `_audit_loop`, `set_native_window`, `get_latest_state` |
| `modules/detector.py` | `load_detector_model`, `detect_objects` |
| `app.py` | `_kiosk_video_render`, `render_live_monitor_view`, controles de inicio y destino |

## Bloque 0. Medicion inicial breve

Realizarlo como preparacion del primer encargo, sin optimizaciones adicionales.

1. Identificar el interprete y las versiones que usa el arranque actual.
2. Separar tiempo de apertura de camara, primer cuadro capturado, primera imagen
   visible y primera deteccion. Usar reloj monotonico para duraciones internas.
3. Registrar si el proceso y el modelo estaban recien iniciados o ya preparados.
   Comparar siempre la misma fuente, escena, resolucion y destino.
4. Obtener una muestra corta de FPS de resultados nuevos, CPU y memoria, usando
   herramientas ya disponibles. No añadir una plataforma de monitoreo.

No reutilizar como referencia definitiva las cifras del entorno que se retiro.
Si no se dispone de camara o escritorio durante la ejecucion, registrar la
limitacion y completar las pruebas simuladas; dejar pendiente la medicion real.

## Bloque 1. Primera imagen antes de la primera inferencia

Archivos permitidos: `modules/auditor.py`, las dos condiciones de visualizacion
y mensajes asociados en `app.py`, y pruebas especificas nuevas.

1. Al recibir el primer cuadro valido, publicar una previsualizacion antes de
   llamar a `detect_objects`. Mantener coherentes imagen RGB y JPEG del estado.
2. Mostrar un estado explicito de inicializacion, sin veredicto de cumplimiento.
   La previsualizacion no debe generar eventos ni evidencias adicionales.
3. Si el destino es nativo, presentar y procesar la primera imagen antes de
   iniciar YOLO. Reutilizar la gestion de ventana existente con un solo
   propietario; no introducir todavia un segundo hilo de interfaz.
4. Reemplazar el filtro arbitrario de 2.000 bytes en productor y consumidores
   por comprobacion del resultado de codificacion y existencia de bytes.
5. Si una codificacion falla, no publicar el JPEG anterior como si fuera nuevo.
6. Respetar una parada solicitada: no volver a publicar actividad tras detener.

Pruebas obligatorias:

- Bloquear deliberadamente el detector simulado con un evento de sincronizacion:
  el estado debe contener la primera imagen antes de liberar la inferencia.
- Un JPEG valido de menos de 2.000 bytes se acepta; un fallo de codificacion no.
- La previsualizacion no llama a persistencia y no indica estado seguro.
- Una parada durante la inicializacion no deja una imagen presentada como activa.
- Comprobar los tres destinos; distinguir simulacion de ventana de prueba real.

Resultado esperado: reducir la espera visual atribuible a la primera inferencia.
Este bloque no promete aumentar los FPS sostenidos ni mantener la ventana nativa
receptiva durante una inferencia larga; eso corresponde al bloque 2.

## Bloque 2. Ventana flotante receptiva

Archivos previstos: `modules/auditor.py`, un modulo pequeño para el visor nativo
y pruebas especificas. La gestion del visor debe ser compatible con el backend
OpenCV/Windows instalado; comprobarla en escritorio antes de darla por validada.

1. Separar la atencion de eventos de ventana del trabajo de inferencia y disco.
2. Concentrar crear, mostrar, consultar eventos y destruir esa ventana en un
   unico hilo propietario. Los controles de Streamlit solo envian solicitudes.
3. Conservar solo la ultima imagen disponible, sin cola creciente de video.
4. Atender cierre y ESC aunque no llegue otro resultado del detector.
5. Cerrar unicamente la ventana del programa; evitar `destroyAllWindows`.
6. Al salir por error o parada, liberar los recursos del visor.

Aceptacion: con el detector simulado bloqueado, la ventana sigue atendiendo
eventos. Abrir, cerrar y reabrir no crea hilos duplicados. Arrastrar y cerrar la
ventana se comprueba tambien manualmente en Windows. Separar eventos no aumenta
por si solo la frecuencia de cuadros analizados.

## Bloque 3. Menos trabajo en los dos visores web

Archivos previstos: `app.py`; `modules/auditor.py` solo si se necesita un
identificador de resultado publicado. No crear otro servidor ni otro framework.

1. Separar la actualizacion del video de las tarjetas y consultas de metricas.
   Mantener inicialmente el intervalo de video actual; metricas aproximadamente
   cada segundo y consultas al cambiar datos o vencer su intervalo.
2. Identificar cada resultado nuevo y compartir el mismo JPEG entre consumidores.
   No ejecutar inferencia ni comprimir de nuevo desde cada pestaña.
3. Evitar trabajo repetido sin borrar la imagen: un fragmento que retorna sin
   renderizar puede retirar sus elementos. Usar un mecanismo compatible con la
   version instalada y comprobar que la imagen anterior permanece visible.
4. Evitar reconstruir diez veces por segundo los paneles estaticos cuando el
   destino elegido es la ventana nativa o el monitor separado.

Aceptacion: abrir ambos visores web mantiene una sola camara y un solo motor de
deteccion; no duplica eventos. La imagen permanece visible cuando no hay cuadro
nuevo. Navegar por otras paginas no detiene el procesamiento.

## Bloque 4. Fotogramas recientes y reinicio seguro

Archivos previstos: `modules/camera.py`, `modules/auditor.py` y pruebas.

1. Añadir secuencia y momento de captura al ultimo cuadro, conservando la API
   existente para los consumidores que todavia la usan.
2. No inferir varias veces sobre la misma captura ni acumular capturas pendientes.
3. Publicar resultado, imagen y tiempos como una instantanea coherente. No
   superponer cajas antiguas sobre otra imagen sin indicar su antiguedad.
4. No iniciar otro trabajador mientras el anterior siga terminando. Un timeout
   de `join` no demuestra que el hilo haya finalizado.
5. Impedir que un trabajador detenido publique resultados en una nueva ejecucion.

Aceptacion: inicio/parada repetidos sin crecimiento de hilos; una captura se
procesa como maximo una vez por trabajador; no reaparecen resultados anteriores
tras detener, reiniciar o desconectar la fuente.

## Bloque 5. Ajustar CPU con evidencia

Archivos previstos: `modules/detector.py` y una prueba de rendimiento acotada.

1. Comparar configuracion actual, 2 hilos y 4 hilos en el entorno restaurado,
   manteniendo modelo, imagen, tracking y tamaño de inferencia iguales.
2. Separar primera llamada de llamadas posteriores; tomar varias muestras
   alternando configuraciones para reducir el efecto de carga externa.
3. Aplicar el limite solo si mejora tiempos o respuesta bajo la misma carga.
   Verificar que el detector no lo sobrescriba durante su inicializacion.
4. No forzar CPU cuando exista aceleracion disponible ni cambiar paquetes.

Aceptacion: comparacion antes/despues documentada, sin degradacion funcional.
Si no mejora, conservar la configuracion anterior. Reducir resolucion o cambiar
el modelo requiere otro experimento porque puede afectar la deteccion de EPP.

## Bloque 6. Escritura fuera del recorrido de visualizacion

Realizarlo si las mediciones muestran pausas asociadas al guardado. Archivos
previstos: `modules/auditor.py` y un escritor modular con pruebas temporales.

1. Enviar eventos confirmados y sus evidencias a un escritor unico.
2. Limitar la cola tanto en cantidad como en memoria; copiar unicamente las
   evidencias necesarias y conservar el identificador de sesion del evento.
3. Definir saturacion y errores explicitamente: no descartar auditorias en
   silencio ni contabilizar como persistido un registro que fallo.
4. Al detener, drenar la cola y cerrar contadores en orden. Si no termina,
   informar el estado pendiente; no afirmar que todo quedo guardado.

Aceptacion: un disco simulado lento no bloquea los eventos del visor; memoria
acotada, errores visibles y correspondencia entre eventos, evidencias y sesion.
No mezclar esta tarea con migraciones o cambios en las reglas de infraccion.

## Comprobacion y entrega de cada bloque

Informar brevemente:

1. Archivos modificados y comportamiento corregido.
2. Pruebas ejecutadas y resultados, diferenciando pruebas simuladas y reales.
3. Mediciones comparables, cuando corresponda, y limitaciones pendientes.
4. Ubicacion del respaldo y archivos nuevos que habria que retirar al revertir.

Para una comprobacion real usar cada destino por separado, despues cambiar de
destino con la camara activa y finalmente abrir el monitor junto al panel.
Comparar espera inicial, antiguedad de imagen, FPS de resultados nuevos y
respuesta al cierre. No confundir frecuencia de refresco con detecciones por
segundo ni prometer un FPS sin medirlo.

Si aparece una regresion, restaurar solo los archivos del bloque afectado desde
su copia, preservando cualquier cambio posterior ajeno. No usar `git reset
--hard`, restauraciones globales, borrado de datos o scripts de apagado masivo.

## Primer encargo listo para el ejecutor

> Lee AGENTS.md y docs/PLAN_RENDIMIENTO_VISORES.md. Usa PROJECT_MAP.md para ubicar
> funciones. Realiza la preparacion breve del bloque 0 e implementa solamente
> el bloque 1: primera imagen antes de YOLO y aceptacion de JPEG validos pequeños
> en los tres destinos. Conserva los cambios existentes y crea respaldo de los
> archivos que edites. No reinstales dependencias, cambies configuraciones de
> agentes, ejecutes otros bloques ni abras subagentes. Usa pruebas simuladas sin
> escribir datos operativos. Entrega el cambio, las comprobaciones y cualquier
> limitacion real de camara o escritorio. Detente al terminar ese bloque.
