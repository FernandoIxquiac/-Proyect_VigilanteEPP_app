# PLAN DE OPTIMIZACIÓN MODULAR — VIGILANTE EPP
> **Documento Operativo para Agentes de Código (`coder-flash`, Claude, Gemini u otros modelos)**  
> **Directiva de Seguridad:** Prohibido el uso de emojis en todo el código, interfaz, comentarios y logs. Utilizar glifos sobrios (●, ■, ◈, ◉, ▲, ≡, ⚙).  
> **Suite de Pruebas Base:** 39 tests unitarios deben mantenerse aprobados al 100% al concluir cada fase (`python -m unittest discover tests`).

---

## Protocolo Obligatorio de Ejecución Inter-Fases

Cualquier agente (incluyendo `coder-flash` o modelos de respaldo) que ejecute este plan **DEBE SEGUIR ESTRICTAMENTE ESTE PROTOCOLO**:

1. **Una sola fase por iteración:** El agente tiene terminantemente prohibido implementar más de una fase a la vez.
2. **Petición de Autorización Previa:** Antes de tocar o editar cualquier archivo de una fase, el agente debe solicitar autorización explícita al usuario indicando:
   - Número y nombre de la fase a iniciar.
   - Archivos que serán modificados o creados.
   - Riesgos mitigados y objetivo exacto.
3. **Pausa para Revisión del Usuario:** Al terminar la fase y verificar que los tests pasen, el agente **debe detenerse de inmediato** y devolver el control al usuario para que este pruebe manualmente la aplicación Streamlit y la ventana nativa de OpenCV.
4. **Actualización de Estado:** El agente debe marcar con `[x]` las tareas completadas en este archivo antes de pasar el turno al usuario.

---

## Estado Global de Avance

- [x] **Fase 1:** Optimización de Persistencia SQLite y Eliminación de Wrappers Fantasma
- [x] **Fase 2:** Optimización del Pipeline Gráfico (Zero-Copy BGR Nativo)
- [x] **Fase 3:** Unificación del Núcleo de Inferencia (`AuditorEngine`)
- [x] **Fase 4:** Desacoplamiento y Modularización de Vistas UI (`app.py` a `modules/views/`)
- [x] **Fase 5:** Higiene de Código Anti-Slop y Consolidación de Estilos CSS
- [x] **Fase 6:** Micro-interacciones y Animaciones Industriales Sobrias (UI / CSS / Plotly)

---

## Fase 1: Optimización de Persistencia SQLite y Eliminación de Wrappers Fantasma

### Objetivo
Eliminar la sobrecarga de consultas redundantes en SQLite por cada evento de auditoría y suprimir la capa de wrappers vacíos en `modules/metrics.py`.

### Diagnóstico de Cuellos de Botella
1. En [modules/database.py](file:///modules/database.py), la función `log_camera_event` invoca `update_session_counters(session_id)` en cada inserción, lo que dispara 2 consultas `COUNT(*)` sobre toda la tabla y un `UPDATE` en `camera_sessions`. Esto cuadruplica el I/O en cada infracción.
2. `get_compliance_stats` ejecuta 3 consultas `COUNT(*)` independientes cuando una única agregación condicional SQL resuelve los 3 valores en un solo escaneo de índice.
3. En [modules/metrics.py](file:///modules/metrics.py), 8 funciones son simples pasarelas de una línea hacia `modules/database.py` sin aportar lógica.

### Tareas Quirúrgicas
- [x] **1.1. Inserción e Incremento Atómico en `modules/database.py`:**
  - En `log_camera_event`, reemplazar la llamada a `update_session_counters` por una sentencia `UPDATE` atómica directa sobre la sesión activa dentro de la misma transacción:
    ```sql
    UPDATE camera_sessions
    SET total_events = total_events + 1,
        infractions_count = infractions_count + CASE WHEN ? IN ('danger', 'warning') THEN 1 ELSE 0 END
    WHERE id = ?;
    ```
  - Mantener `update_session_counters` únicamente como utilidad de recalibración/reparación para cierre de sesiones o mantenimiento.
- [x] **1.2. Agregación Condicional en `get_compliance_stats`:**
  - Reemplazar los 3 `SELECT COUNT(*)` por una única consulta agregada:
    ```sql
    SELECT 
        COUNT(*),
        COALESCE(SUM(CASE WHEN status = 'safe' THEN 1 ELSE 0 END), 0),
        COALESCE(SUM(CASE WHEN status IN ('danger', 'warning') THEN 1 ELSE 0 END), 0)
    FROM camera_events
    WHERE session_id = ?; -- (o sin WHERE para histórico global)
    ```
- [x] **1.3. Poda de Wrappers en `modules/metrics.py`:**
  - Eliminar los wrappers redundantes: `db_get_compliance_stats`, `db_get_recent_incidents`, `db_get_history_dataframe`, `db_get_detailed_events_dataframe`, `db_get_hourly_risk_distribution`, `db_get_all_sessions_list`, `db_get_active_session_info`, `db_close_active_session`.
  - Re-exportar limpiamente o actualizar las importaciones en `app.py` directamente desde `modules.database`.
  - Preservar en `modules/metrics.py` únicamente: `init_session_state`, `reset_session_state`, `record_camera_audit` y `calculate_roi`.

### Criterios de Aceptación y Anti-Errores
- Los 39 tests automáticos deben pasar sin errores: `python -m unittest discover tests`.
- Verificar que `test_audit_writer.py` registre y confirme transacciones sin bloqueos WAL.
- Ninguna función pública eliminada debe romper llamadas en `app.py`.

---

## Fase 2: Optimización del Pipeline Gráfico (Zero-Copy BGR Nativo)

### Objetivo
Eliminar el cuello de botella de doble conversión de color (`BGR -> RGB -> BGR`) en cada cuadro procesado a 20–30 FPS.

### Diagnóstico de Cuellos de Botella
- La inferencia YOLOv8 en [modules/detector.py](file:///modules/detector.py) genera un array BGR (`results[0].plot()`).
- Inmediatamente se convierte a RGB (`cv2.cvtColor(annotated_bgr, cv2.COLOR_BGR2RGB)`).
- Luego, en [modules/auditor.py](file:///modules/auditor.py) y [modules/demo_video.py](file:///modules/demo_video.py), se dibujan etiquetas y se vuelve a convertir a BGR (`cv2.cvtColor(frame_rgb, cv2.COLOR_RGB2BGR)`) para enviarlo a la ventana nativa de escritorio `LatestFrameNativeViewer`.
- Dado que el navegador web ya no renderiza video continuo vía WebRTC/MJPEG, transformar a RGB y regresar a BGR desperdicia ciclos de CPU y ancho de banda de memoria en cada cuadro.

### Tareas Quirúrgicas
- [x] **2.1. Soporte Nativo BGR en `modules/detector.py`:**
  - Modificar `detect_objects` añadiendo el parámetro `return_rgb=False` por defecto o adaptarlo para devolver la imagen anotada directamente en BGR (`annotated_bgr`).
  - Si un consumidor explícito requiere RGB (ej. previsualización estática en Streamlit con `st.image`), convertir solo bajo demanda.
- [x] **2.2. Anotación Directa en BGR en `modules/auditor.py`:**
  - Adaptar el bucle de `_audit_loop_impl` para trabajar sobre el fotograma BGR nativo.
  - Asegurar que los colores OpenCV usados en `cv2.rectangle` y `cv2.putText` correspondan al formato BGR (ej. Verde seguro: `(0, 220, 110)`, Rojo peligro: `(0, 60, 240)`).
  - Publicar directamente `self._native_viewer.publish(annotated_bgr)` sin llamada a `cv2.cvtColor`.
- [x] **2.3. Anotación Directa en BGR en `modules/demo_video.py`:**
  - Actualizar `_annotate_demo_frame` y `display_static_image` para recibir y dibujar directamente en búfer BGR.
  - Enviar directamente a `self._viewer.publish(annotated_bgr)`.

### Criterios de Aceptación y Anti-Errores
- Los 39 tests automáticos deben pasar sin errores: `python -m unittest discover tests`.
- Verificar en `test_auditor_first_frame.py` y `test_demo_video.py` que la secuencia de cuadros y entrega $O(1)$ sea íntegra.
- Los colores en la ventana flotante nativa deben mantenerse fidedignos (verde para operarios conformes, rojo para infracciones, azul para el HUD superior).

---

## Fase 3: Unificación del Núcleo de Inferencia (`AuditorEngine`)

### Objetivo
Erradicar la duplicación de ~400 líneas de código idéntico entre [modules/auditor.py](file:///modules/auditor.py) y [modules/demo_video.py](file:///modules/demo_video.py).

### Diagnóstico de Cuellos de Botella
- Ambos servicios implementan bucles idénticos de lectura de cámara, llamada a detector, tracking espacial, anotación de recuadros, control de cadencia FPS y control de `LatestFrameNativeViewer`.
- La única discrepancia es que `LiveAuditorService` envía eventos a `AuditEventWriter` (SQLite + disco) con `session_id`, mientras `DemoVideoService` almacena eventos en memoria (`collections.deque(maxlen=6)`).

### Tareas Quirúrgicas
- [x] **3.1. Creación de `modules/auditor_core.py`:**
  - Extraer la clase base común `BaseAuditorService` con:
    - Gestión de hilo demonio (`start`, `stop`, `is_running`, `is_busy`).
    - Pacing de FPS y medición de latencia.
    - Anotación de cajas delimitadoras y banner HUD unificado.
    - Interfaz abstracta o hook de evento: `_on_worker_event_confirmed(event_payload)`.
    - Comunicación thread-safe con `LatestFrameNativeViewer`.
- [x] **3.2. Refactorización de `LiveAuditorService`:**
  - Heredar de `BaseAuditorService` e implementar `_on_worker_event_confirmed` conectándolo a `AuditEventWriter` y base de datos SQLite.
  - Mantener exactamente las mismas firmas públicas (`start`, `stop`, `update_config`, `get_latest_state`, etc.) para no romper dependencias en la UI ni en los tests.
- [x] **3.3. Refactorización de `DemoVideoService`:**
  - Heredar de `BaseAuditorService` e implementar `_on_worker_event_confirmed` registrando el evento en `collections.deque(maxlen=6)`.
  - Preservar métodos auxiliares propios de sandbox como `display_static_image`.

### Criterios de Aceptación y Anti-Errores
- Los 39 tests automáticos deben pasar sin errores: `python -m unittest discover tests`.
- Preservar las firmas de los singletons `@st.cache_resource`: `get_live_auditor()` y `get_demo_video_service()`.
- Garantizar que la exclusión mutua `CAMERA_MODE_LOCK` siga funcionando sin deadlocks al alternar entre Demostración y En Vivo.

---

## Fase 4: Desacoplamiento y Modularización de Vistas UI (`app.py`)

### Objetivo
Reducir el archivo monolítico [app.py](file:///app.py) de 1,154 líneas a un orquestador limpio y declarativo de menos de 200 líneas.

### Diagnóstico de Cuellos de Botella
- `app.py` contiene lógica de renderizado masiva, diálogos modales, selectores de fuentes duplicados, llamadas SQL directas y fragmentos reactivos repetidos.
- Cualquier fallo de sintaxis en una sección afecta a toda la aplicación Streamlit.

### Tareas Quirúrgicas
- [x] **4.1. Crear directorio `modules/views/` con submódulos independientes:**
  - `modules/views/__init__.py`.
  - `modules/views/components.py`: Componentes visuales reutilizables:
    - Control de encendido/apagado y selector de dispositivo de cámara.
    - Plantillas de conexión rápida RTSP/IP.
    - Fragmentos reactivos de tarjetas de estado y bloque de 3 métricas.
  - `modules/views/demo_view.py`: Función `render_demo_view(model, is_dark, cfg)` conteniendo la lógica de demostración, archivos subidos y sintéticos.
  - `modules/views/live_view.py`: Función `render_live_view(model, is_dark, cfg)` conteniendo el análisis en vivo y supervisión de planta.
  - `modules/views/stats_view.py`: Función `render_stats_view(is_dark)` con selectores de turno, gráficos SPC y calculadora de ROI.
  - `modules/views/reports_view.py`: Función `render_reports_view(is_dark)` con diagnósticos periciales, bitácora forense, galería de capturas y exportación de informes HTML/CSV.
  - `modules/views/config_dialog.py`: Modal emergente `@st.dialog("Configuracion del Sistema")`.
- [x] **4.2. Adelgazamiento de `app.py`:**
  - Mantener en `app.py` únicamente:
    - Configuración de página (`st.set_page_config`).
    - Inicialización de `session_state` y sincronización de tema.
    - Carga del modelo IA (`load_detector_model`).
    - Barra lateral (`st.sidebar`) y enrutador condicional:
      ```python
      if "Demostracion" in page:
          render_demo_view(model, is_dark, cfg)
      elif "Analisis en Vivo" in page:
          render_live_view(model, is_dark, cfg)
      elif "Estadisticas" in page:
          render_stats_view(is_dark)
      elif "Reportes" in page:
          render_reports_view(is_dark)
      ```

### Criterios de Aceptación y Anti-Errores
- Los 39 tests automáticos deben pasar sin errores: `python -m unittest discover tests`.
- Comprobar que `tests/test_app_navigation.py` pase al 100%.
- Verificar que el cambio de tema (Oscuro/Claro) y el modo riel (72px/250px) sigan funcionando de forma reactiva sin parpadeos.

---

## Fase 5: Higiene de Código Anti-Slop y Consolidación de Estilos CSS

### Objetivo
Eliminar estilos en línea desordenados, retirar comentarios decorativos generados por IA y cumplir estrictamente las directrices de `antislop-code` y `antislop-ui`.

### Diagnóstico de Cuellos de Botella
- Cientos de etiquetas `<div style="...">` con valores hardcodeados dispersas en el código de vistas.
- Banners decorativos con caracteres repetidos (`# -----------------`, `# =====================`) en cabeceras de funciones.

### Tareas Quirúrgicas
- [x] **5.1. Clases Utilitarias en `styles/styles.py`:**
  - Reemplazar estilos en línea por clases CSS semánticas vinculadas a variables de tema (`.hud-card`, `.section-header`, `.badge-indicator`, `.kpi-subtext`).
- [x] **5.2. Limpieza de Comentarios (`antislop-code`):**
  - Retirar banners de caracteres repetidos (`===`, `---`).
  - Eliminar comentarios que solo repiten la línea de código siguiente (ej. `# Selector de sesión` encima de `st.selectbox`).
  - Preservar exclusivamente comentarios de restricciones de concurrencia, seguridad o justificaciones técnicas no evidentes.
- [x] **5.3. Auditoría Final de Reglas:**
  - Verificar CERO emojis en todo el repositorio.
  - Verificar que el archivo `PROJECT_MAP.md` quede actualizado reflejando la nueva estructura modular de `modules/views/` y `modules/auditor_core.py`.

### Criterios de Aceptación y Anti-Errores
- Ejecutar la suite completa: `python -m unittest discover tests`.
- Compilación sintáctica global: `python -m py_compile app.py modules/*.py modules/views/*.py styles/*.py`.
- Verificación manual en navegador de la fluidez global de la aplicación.

---

## Fase 6: Micro-interacciones y Animaciones Industriales Sobrias (UI / CSS / Plotly)

### Objetivo
Implementar micro-animaciones sobrias y transiciones reactivas en CSS y Plotly para comunicar telemetría y estado operativo en tiempo real (cámara activa, cambios de nivel de riesgo en semáforo, actualización de gráficas y llegada de nuevos incidentes) sin degradar el rendimiento y cumpliendo estrictamente los filtros de anti-slop.

### Justificación de Propósito Funcional (Anti-Slop R-19 / R-13 / R-01)
- Cada animación responde a un evento de negocio específico:
  1. **Indicador de cámara activa:** Proporciona certeza visual inmediata de que la captura de video está procesando cuadros.
  2. **Tarjeta de ventana nativa activa:** Confirma que el visor OpenCV desacoplado está operando.
  3. **Tarjeta semáforo (crítico):** Un pulso de advertencia de 1.2s en el borde enfoca la atención del operador ante eventos peligrosos.
  4. **Bitácora forense:** Desplazamiento sutil hacia abajo (`slide-in`) al agregarse una nueva evidencia.
  5. **Gráficos Plotly:** La interpolación fluida evita saltos bruscos cada vez que el fragmento reactivo actualiza contadores.
  6. **Cabecera institucional:** El latido sutil en el badge de sistema activo confirma que el hilo de inferencia no está bloqueado.
- Topes de dosis estrictos: Cero brillos de pantalla completa, cero neones estridentes, aceleración 100% por GPU en navegador.

### Tareas Quirúrgicas
- [x] **6.1. Definición de Keyframes y Clases Semánticas en `styles/styles.py`:**
  - Agregar `@keyframes pulse-live` y la clase `.status-live-dot` (pulso circular verde de 9px).
  - Agregar `@keyframes hud-scanline` y la clase `.hud-card-active` con acento lateral pulsante.
  - Agregar `@keyframes border-alert-flash` y la clase `.status-card-danger` con destello de borde de 1.2s en rojo semafórico.
  - Agregar `@keyframes incident-slide` y la clase `.incident-card-animated` con transición de entrada suave (0.25s).
  - Agregar `@keyframes badge-heartbeat` y la clase `.header-active-badge` en la cabecera.
  - Asegurar compatibilidad de contraste y variables cromáticas en Modo Claro y Modo Oscuro (R-34).
- [x] **6.2. Interpolación y Transición Fluida en `modules/charts.py`:**
  - Configurar en `create_spc_control_chart` y `create_severity_bar_chart`:
    - `uirevision="constant_session_zoom"` para retener el estado y perspectiva del usuario durante refrescos de fragmentos.
    - `transition={"duration": 500, "easing": "cubic-in-out"}` para suavizar la actualización de líneas y barras.
- [x] **6.3. Integración en Componentes y Vistas UI:**
  - En `styles/styles.py`: actualizar `render_status_card` para aplicar la clase animada cuando el estado sea `danger`.
  - En `styles/styles.py`: actualizar `render_top_header` para aplicar `.header-active-badge` en el indicador de sistema activo.
  - En `modules/views/components.py`: actualizar `render_desktop_window_card` para aceptar un flag opcional `is_active: bool = False` que inyecte la clase `.hud-card-active`.
  - En `modules/views/live_view.py`: integrar `<span class="status-live-dot"></span>` en el indicador de cámara activa, pasar `is_active=True` a `render_desktop_window_card` y aplicar la animación en las tarjetas de incidentes.
- [x] **6.4. Verificación y Control de Calidad:**
  - Cero emojis en todos los archivos modificados (prohibición estricta).
  - Ejecutar la suite de pruebas unitarias: `python -m unittest discover tests` (39/39 OK).
  - Compilación sintáctica sin errores: `python -m py_compile app.py modules/*.py modules/views/*.py styles/*.py`.

### Criterios de Aceptación y Anti-Errores
- Los 39 tests automáticos deben pasar sin errores: `python -m unittest discover tests`.
- No alterar la lógica de hilos de inferencia ni la persistencia SQLite en `modules/auditor.py` o `modules/database.py`.
- Las animaciones deben verse fluidas y sobrias tanto en tema claro como oscuro sin desplazar componentes.

---

## Instrucciones de Inicio para el Agente Operador (`coder-flash` / Modelo Activo)

Cuando estés listo para trabajar:
1. Lee este archivo completo y revisa el estado de las casillas `[ ]`.
2. Identifica la **primera fase pendiente** (ej. Fase 1).
3. **DETENTE**: No escribas código todavía. Presenta al usuario un mensaje breve y técnico solicitando su autorización explícita para comenzar esa fase específica.
4. Una vez que el usuario responda autorizando la fase, procede con la implementación quirúrgica, ejecuta los tests y devuélvele el control para su revisión.
