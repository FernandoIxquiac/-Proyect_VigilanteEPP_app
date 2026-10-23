# PROJECT MAP — Vigilante EPP (SafeGuard AI)
> **Índice de Contexto Rápido para Agentes y Desarrolladores**  
> *Consulte este archivo al inicio de una sesión para ubicar arquitectura, módulos y flujos sin re-escanear todo el código.*

---

## 1. Visión General & Propósito
**Vigilante EPP** es una aplicación de visión artificial para la supervisión y auditoría en tiempo real del uso de Equipo de Protección Personal (casco, chaleco reflectante) en plantas industriales y obras.

* **Modo de Operación:** 100% Local / Offline.
* **Interfaz de Usuario:** Dashboard interactivo en Streamlit organizado mediante barra de navegación lateral permanente con modo riel colapsable (72px compacto / 250px expandido), botones minimalistas (Ghost/Flat) con iconos vectoriales SVG locales y diálogo modal de configuración:
  1. `Demostración` (icono `device-desktop`): Sandbox interactivo para probar el modelo en fotografías o escenas sintéticas sin almacenar datos en la base de datos.
  2. `Análisis en Vivo` (icono `video`): Monitoreo en directo por webcam/RTSP con tracking multi-operario (ByteTrack), HUD semafórico y registro automático de infracciones.
  3. `Estadísticas` (icono `chart-bar`): Panel gerencial con KPIs, gráficos de control estadístico (SPC Shewhart Run Chart), distribución de severidad cromática y calculadora interactiva de ROI.
  4. `Reportes` (icono `file-text`): Dictamen pericial automatizado (ISO 45001 / OSHA) con tarjeta dinámica sensible al tema, bitácora forense de auditoría y exportación oficial en HTML y CSV.
  5. `Configuración` (icono `settings`): Modal emergente compacto (@st.dialog) en dos columnas para alternar tema visual, ajustar sensibilidad/umbral (%) y activar/desactivar filtros de EPP sin scroll vertical.
  6. `Riel Permanente` (icono `chevrons-left`): Control reactivo para alternar entre vista completa y riel estrecho de solo iconos sin ocultar la barra de la pantalla.

---

## 2. Stack Tecnológico

| Capa | Tecnologías | Notas |
|---|---|---|
| **Lenguaje** | Python 3.9+ | Multiplataforma (Windows y Linux) |
| **Frontend / UI** | Streamlit (≥ 1.30) | Componentes reactivos, SessionState, vistas modulares en `modules/views/` |
| **Visión Artificial** | Ultralytics YOLOv8, OpenCV 4.8+ | Inferencia local BGR nativa (zero-copy) en CPU o GPU (CUDA) |
| **Núcleo de Inferencia** | `modules/auditor_core.py` | Clase base `BaseAuditorService` con pacing de FPS y HUD unificado |
| **Tracking** | ByteTrack (MOT) | Persistencia de IDs entre frames con filtro anti-parpadeo |
| **Visualización** | Plotly (≥ 5.0) | Gráficos de Control Estadístico de Procesos (SPC) y barras cromáticas |
| **Base de Datos** | SQLite (`data/vigilante_epp.db`) | Esquema relacional normalizado con modo WAL e incrementos atómicos |
| **Estilos** | CSS personalizado (`styles/styles.py`) | Variables de tema Dark/Light, clases utilitarias semánticas y badges |
| **Reportes** | HTML5 / CSS auto-contenido | Convertibles a PDF (ISO 45001 / OSHA 1910) y CSV forense |

---

## 3. Diagrama de Arquitectura y Flujo de Datos

```mermaid
flowchart TD
    subgraph Entrada ["1. Fuentes de Entrada"]
        CAM["Webcam USB / RTSP (Flujo en Vivo)"]
        IMG["Imágenes Subidas / Sintéticas (Sandbox)"]
    end

    subgraph Captura ["2. Captura Desacoplada Multihilo"]
        STREAM["modules/camera.py (CameraStreamManager / ThreadedCamera)"]
        SOURCES["modules/camera_sources.py (CAMERA_MODE_LOCK & Resolver)"]
    end

    subgraph Core ["3. Núcleo Común de Inferencia BGR"]
        CORE_AUDITOR["modules/auditor_core.py (BaseAuditorService & annotate_auditor_frame)"]
        AUDITOR["modules/auditor.py (LiveAuditorService)"]
        DEMO_VIDEO["modules/demo_video.py (DemoVideoService)"]
        YOLO["YOLOv8 BGR Nativo (models/ppe_model.pt)"]
        TRACK["WorkerTrackManager (ByteTrack MOT)"]
        SPATIAL["Análisis Espacial (Caja Persona vs EPP)"]
        VIEWER["modules/native_viewer.py (LatestFrameNativeViewer Win32 50 FPS)"]
        WIN["Ventana Flotante de Escritorio (cv2.imshow)"]
    end

    subgraph Logica ["4. Persistencia Asíncrona SQLite WAL"]
        A_WRITER["modules/audit_writer.py (AuditEventWriter - Cola Asíncrona)"]
        METRICS["modules/metrics.py (Cálculos ROI & Sesión)"]
        DB[(data/vigilante_epp.db - Modo WAL + UPDATE Atómico)]
        CAPS[("captures/ (Evidencias JPG)")]
    end

    subgraph Presentacion ["5. Vistas Desacopladas y Dashboard"]
        APP["app.py (Orquestador Declarativo < 200 líneas)"]
        VIEWS["modules/views/ (demo, live, stats, reports, config, components)"]
        CHARTS["modules/charts.py (SPC & Plotly)"]
        REP["modules/report_generator.py (HTML Report Preliminar/Cerrado)"]
        STYLES["styles/styles.py (CSS Semántico & Cockpit)"]
    end

    CAM --> SOURCES
    SOURCES --> STREAM
    STREAM --> CORE_AUDITOR
    CORE_AUDITOR --> AUDITOR
    CORE_AUDITOR --> DEMO_VIDEO
    AUDITOR --> YOLO
    DEMO_VIDEO -->|Inferencia y Tracking MOT en RAM| YOLO
    YOLO --> TRACK
    TRACK --> SPATIAL
    SPATIAL --> CORE_AUDITOR
    CORE_AUDITOR -.-> VIEWER
    VIEWER -->|Repintado Continuo 50 FPS| WIN
    AUDITOR -->|Hook Asíncrono| A_WRITER
    A_WRITER -->|Transacciones Atómicas| DB
    A_WRITER -.->|Infracción Crítica| CAPS
    IMG --> DEMO_VIDEO
    APP --> VIEWS
    VIEWS -->|get_latest_state O(1)| AUDITOR
    VIEWS -->|get_state O(1)| DEMO_VIDEO
    DB --> VIEWS
    METRICS --> VIEWS
    METRICS --> CHARTS
    CHARTS --> VIEWS
    DB --> REP
    STYLES --> APP
    STYLES --> VIEWS
```

---

## 4. Directorio y Mapa de Módulos

```
PROYECTO EPP/
├── app.py                      # Orquestador declarativo (< 200 líneas): routing, sesión y sidebar
├── requirements.txt            # Dependencias del entorno (Streamlit, YOLOv8, OpenCV, Plotly, etc.)
├── README.md                   # Documentación general para usuarios y presentación
├── PROJECT_MAP.md              # [ESTE ARCHIVO] Mapa de arquitectura e indexación rápida
├── PLAN.md                     # Plan de optimización modular y registro de fases operativas
├── LICENSE                     # Licencia de código abierto MIT
├── .gitignore                  # Exclusiones de Git (BD local, capturas, entornos, temporales)
├── .gitattributes              # Normalización de saltos de línea (CRLF para .bat)
├── .streamlit/
│   └── config.toml             # Configuración visual de Streamlit (paleta, layout y tipografía)
├── assets/
│   ├── logo.jpg                # Logo institucional para reportes y cabecera (fallback)
│   ├── logo.svg                # Logo vectorial institucional principal
│   └── *.svg                   # Catálogo local de iconos vectoriales SVG (navegación, estado y archivos)
├── docs/
│   ├── DESIGN.md               # Especificación completa del sistema de diseño industrial
│   ├── proyecto_base.md        # Especificación técnica base y guía de pitch de feria
│   └── PLAN_RENDIMIENTO_VISORES.md # Bitácora técnica y registro de arquitectura
├── models/
│   └── ppe_model.pt            # Pesos del modelo YOLOv8 entrenado para EPP (~6.2 MB)
├── data/                       # [Excluido en Git - Autogenerado]
│   └── vigilante_epp.db        # Base de datos SQLite (sesiones + infracciones)
├── captures/                   # [Excluido en Git - Autogenerado]
│   └── *.jpg                   # Evidencias fotográficas JPG de infracciones
├── scripts/                    # Scripts de ejecución rápida multiplataforma
│   ├── 1_instalar.bat          # Pip install requirements (Windows)
│   ├── 1_instalar_linux.sh     # Instalación optimizada PyTorch CPU (Linux)
│   ├── 2_iniciar.bat           # Ejecuta 'streamlit run app.py' (Windows)
│   ├── 3_apagar.bat            # Mata procesos de Streamlit/Python y libera cámara (Windows)
│   ├── 4_publicar_github.bat   # Verificaciones de seguridad, git add, commit y push (Windows)
│   └── 5_actualizar.bat        # Git pull sincronizado (Windows)
├── styles/                     # Capa de diseño y presentación
│   ├── __init__.py
│   ├── icons.py                # Gestor de iconos vectoriales SVG con soporte para tamaño, trazo y color dinámico
│   └── styles.py               # Inyección CSS personalizada, clases utilitarias, header y status cards
├── modules/                    # Lógica modular de backend desacoplada
│   ├── __init__.py
│   ├── audit_writer.py         # Persistencia asíncrona desacoplada en segundo plano para SQLite y disco
│   ├── auditor_core.py         # Núcleo base común de inferencia (BaseAuditorService) y renderizado BGR
│   ├── auditor.py              # Servicio de auditoría en vivo (LiveAuditorService) conectado a SQLite
│   ├── camera.py               # Captura multihilo desacoplada, buffer O(1) y gestión singleton de hardware
│   ├── camera_sources.py       # Centralización de fuentes de video y exclusión mutua de hardware (CAMERA_MODE_LOCK)
│   ├── charts.py               # Gráficos de Control Estadístico de Procesos (SPC) y severidad con Plotly
│   ├── database.py             # Capa SQLite WAL optimizada con incrementos atómicos y consultas agregadas
│   ├── demo_video.py           # Servicio de demostración en memoria: video y fotos, cero persistencia en BD
│   ├── detector.py             # Inferencia YOLOv8 BGR nativo, lógica espacial y semaforización
│   ├── metrics.py              # Inicialización de estado y cálculo interactivo de ROI
│   ├── native_viewer.py        # Visor OpenCV con hilo Win32 dedicado, sincronización O(1) y 50 FPS
│   ├── report_generator.py     # Informes periciales HTML (dictamen preliminar/cerrado) exportables a PDF
│   ├── samples.py              # Generador de escenarios fotográficos sintéticos para demostración
│   ├── tracker_manager.py      # Tracking persistente ByteTrack, anti-parpadeo y cooldown de alertas
│   └── views/                  # Vistas modulares y componentes de interfaz Streamlit
│       ├── __init__.py         # Exportaciones de vistas
│       ├── components.py       # Plantillas RTSP, escaneo de dispositivos y tarjetas HUD
│       ├── config_dialog.py    # Diálogo modal emergente (@st.dialog)
│       ├── demo_view.py        # Vista de demostración y sandbox interactivo
│       ├── live_view.py        # Vista de análisis y supervisión en vivo
│       ├── stats_view.py       # Vista de estadísticas gerenciales, gráficos SPC y calculadora ROI
│       └── reports_view.py     # Vista de dictamen pericial, bitácora forense y exportación
└── tests/                      # Suite de pruebas automatizadas (39 pruebas unitarias al 100% OK)
    ├── test_app_navigation.py  # Navegación, vistas desacopladas y estado reactivo de Streamlit
    ├── test_audit_writer.py    # Persistencia asíncrona y transaccional
    ├── test_auditor_first_frame.py # Entrega inmediata de previsualización y ciclo de vida de ventana nativa
    ├── test_camera_frame_sequence.py # Secuencialidad y consistencia de captura
    ├── test_camera_sources.py  # Detección dinámica de cámaras, normalización IP y presets
    └── test_demo_video.py      # Modo demostración, cero persistencia y visualización
```

---

### Índice Rápido de Símbolos

#### [`modules/auditor_core.py`](file:///modules/auditor_core.py) — Núcleo Común de Inferencia
* `BaseAuditorService`: Clase abstracta que unifica el ciclo de vida del hilo demonio, captura y pacing de FPS, entrega inmediata del primer cuadro preview, inferencia y tracking espacial en BGR nativo, y hook abstracto `_on_worker_event_confirmed(event_payload)`.
* `annotate_auditor_frame(frame_bgr, workers_data, status, title, message, ...)`: Función pura desacoplada para renderizado gráfico BGR de recuadros de operarios, etiquetas y banner HUD superior.

#### [`modules/auditor.py`](file:///modules/auditor.py) — Servicio de Auditoría en Vivo
* `LiveAuditorService`: Especialización de `BaseAuditorService` que implementa `_on_worker_event_confirmed` enviando eventos a `AuditEventWriter` para persistencia transaccional en SQLite y almacenamiento de evidencias fotográficas en disco.
* `get_live_auditor()`: Proveedor singleton con `@st.cache_resource`.

#### [`modules/demo_video.py`](file:///modules/demo_video.py) — Sandbox de Demostración
* `DemoVideoService`: Especialización de `BaseAuditorService` que implementa `_on_worker_event_confirmed` registrando eventos en una cola circular en RAM (`collections.deque(maxlen=6)`), con cero persistencia en disco o base de datos.
* `display_static_image(...)`: Procesa e inyecta imágenes estáticas o sintéticas directamente en la ventana de escritorio.
* `get_demo_video_service()`: Proveedor singleton con `@st.cache_resource`.

#### [`modules/detector.py`](file:///modules/detector.py) — Inferencia y Visión Artificial BGR
* `detect_objects(..., return_rgb=False)`: Pipeline BGR nativo zero-copy que evita la sobrecarga de conversiones de color intermedias.
* `analyze_workers_spatial(...)`: Asociación espacial geométrica de operarios con cascos y chalecos.
* `evaluate_compliance(...)`: Semáforo integral de seguridad (`safe`, `warning`, `danger`, `standby`).

#### [`modules/database.py`](file:///modules/database.py) — Persistencia SQLite WAL Optimizada
* `log_camera_event(...)`: Inserción transaccional atómica que actualiza los contadores de la sesión activa en una sola sentencia SQL, reduciendo drásticamente las operaciones I/O por infracción.
* `get_compliance_stats(session_id)`: Agregación condicional única mediante `SUM(CASE ...)` en una sola consulta SQL.

#### [`modules/metrics.py`](file:///modules/metrics.py) — Estado de Sesión y Analítica
* `init_session_state()` / `reset_session_state()`: Inicialización y reinicio del estado reactivo de Streamlit.
* `calculate_roi(num_workers, avg_fine)`: Estimación de retorno de inversión y ahorro anual frente a sanciones laborales/OSHA.

#### [`modules/views/`](file:///modules/views/) — Vistas Desacopladas
* `components.py`: Componentes visuales reutilizables (`render_stream_presets`, `render_device_scanner`, `render_desktop_window_card`).
* `config_dialog.py`: Diálogo modal `@st.dialog("Configuracion del Sistema")` para parámetros del sistema.
* `demo_view.py`: `render_demo_view(model, is_dark, cfg)` para sandbox de demostración y pruebas multimedia.
* `live_view.py`: `render_live_view(model, is_dark, cfg)` para supervisión en vivo y control de cámara.
* `stats_view.py`: `render_stats_view(is_dark)` para métricas gerenciales, control SPC y ROI.
* `reports_view.py`: `render_reports_view(is_dark)` para dictamen pericial, bitácora forense y exportación.

#### [`app.py`](file:///app.py) — Orquestador Central
* Orquestador limpio de menos de 200 líneas que gestiona la configuración de página, sincronización de tema, barra lateral con modo riel permanente y enrutador condicional a cada vista modular.

---

## 5. Esquema de Datos (`vigilante_epp.db`)

### Tabla Maestra: `camera_sessions`
| Columna | Tipo | Descripción |
|---|---|---|
| `id` | INTEGER (PK AUTOINCREMENT) | Identificador único del turno/sesión |
| `session_name` | TEXT NOT NULL | Nombre descriptivo del turno |
| `start_time` | DATETIME NOT NULL | Inicio de la supervisión |
| `end_time` | DATETIME | Cierre de la supervisión |
| `status` | TEXT DEFAULT 'active' | Estado del turno: `'active'` o `'closed'` |
| `total_events` | INTEGER DEFAULT 0 | Contador acumulado de eventos registrados |
| `infractions_count` | INTEGER DEFAULT 0 | Contador de infracciones de seguridad |
| `created_at` | DATETIME | Timestamp de creación |

### Tabla Transaccional: `camera_events`
| Columna | Tipo | Descripción |
|---|---|---|
| `id` | INTEGER (PK AUTOINCREMENT) | Identificador único del evento |
| `session_id` | INTEGER (FK) | Referencia a `camera_sessions(id)` con ON DELETE CASCADE |
| `worker_id` | TEXT DEFAULT 'N/A' | ID persistente del trabajador (ByteTrack, ej. '#Operario-01') |
| `timestamp` | DATETIME NOT NULL | Fecha y hora exacta del suceso |
| `category` | TEXT NOT NULL | Clasificación (`'Cumplimiento Total (OK)'`, `'Sin Casco'`, `'Sin Chaleco'`, etc.) |
| `details` | TEXT | Descripción pericial detallada |
| `status` | TEXT NOT NULL | Nivel de riesgo (`'safe'`, `'danger'`, `'warning'`) |
| `personnel_count` | INTEGER DEFAULT 1 | Cantidad de trabajadores involucrados |
| `confidence` | REAL DEFAULT 0.0 | Confianza de la detección IA (%) |
| `evidence_path` | TEXT | Ruta local a la captura JPG de evidencia |

---

## 6. Checklist de Publicación en GitHub

Antes de ejecutar `scripts/4_publicar_github.bat`, verificar:
1. **Archivos Sensibles Ignorados:** Verificar que `data/` (`*.db`) y `captures/` (`*.jpg`) no estén en el staged de Git (`git status`).
2. **Dependencias Completas:** Asegurar que `requirements.txt` incluya `plotly>=5.0.0`.
3. **Tamaño del Modelo IA:** `models/ppe_model.pt` pesa ~6.25 MB (dentro del límite de 100 MB).
4. **Scripts con Permisos / Formato:** Scripts `.bat` preservan formato CRLF y scripts `.sh` formato LF.
5. **Cero Emojis:** Prohibición estricta de emojis en todo el repositorio.
