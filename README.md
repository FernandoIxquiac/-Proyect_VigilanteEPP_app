# Vigilante EPP — SafeGuard AI

<div align="center">

**Sistema Inteligente de Detección de Equipos de Protección Personal en Tiempo Real**

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776ab?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.50%2B-ff4b4b?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-00C4CC?style=for-the-badge&logo=yolo&logoColor=white)](https://ultralytics.com)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8%2B-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

*Prevención proactiva de accidentes laborales con Inteligencia Artificial · Feria de Proyectos 2026*

</div>

---

## Tabla de Contenidos

- [¿Qué es Vigilante EPP?](#que-es-vigilante-epp)
- [Demostración](#demostración)
- [Características Principales](#características-principales)
- [Stack Tecnológico](#stack-tecnológico)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Instalación y Ejecución](#instalación-y-ejecución)
- [Cómo Funciona](#cómo-funciona)
- [Módulos del Sistema](#módulos-del-sistema)
- [Impacto y ROI](#impacto-y-roi)
- [Contribuir](#contribuir)
- [Licencia](#licencia)

---

## <a name="que-es-vigilante-epp"></a>¿Qué es Vigilante EPP?

**Vigilante EPP** es una plataforma de visión por computadora que analiza transmisiones de video en tiempo real para detectar automáticamente la **presencia o ausencia de Equipos de Protección Personal (EPP)** — casco de seguridad y chaleco reflectante — en entornos industriales.

> **Problema Real:** En sectores como minería, manufactura y construcción, más del **40% de los accidentes graves** ocurren por falta de uso o uso indebido de EPP. La supervisión humana tradicional es intermitente, costosa y propensa al error.

> **Nuestra Solución:** Monitoreo continuo con IA, alertas visuales inmediatas, trazabilidad por operario y generación automática de informes forenses — sin necesidad de servidores externos ni infraestructura costosa.

---

## Demostración

| Sección / Componente | Icono Vectorial | Descripción |
|---|:---:|---|
| **Demostración** | `device-desktop.svg` | Prueba imágenes y escenas sintéticas, o abre una ventana local con video y marcas de detección. El video no crea auditorías ni guarda datos. |
| **Análisis en Vivo** | `video.svg` | Monitoreo por webcam o flujo RTSP/IP en una ventana local de escritorio. El navegador muestra controles, estado y métricas, sin transmitir el video. |
| **Estadísticas** | `chart-bar.svg` | Control Estadístico de Procesos (SPC Shewhart Run Chart), distribución de severidad cromática y calculadora interactiva de ROI. |
| **Reportes** | `file-text.svg` | Dictamen pericial automatizado (ISO 45001 / OSHA) con tarjeta de apego normativo dinámica y exportación oficial en HTML/CSV. |
| **Configuración** | `settings.svg` | Modal emergente compacto (@st.dialog) en 2 columnas para alternar tema (Oscuro/Claro), umbral de sensibilidad y filtros de EPP. |
| **Riel Permanente** | `chevrons-left.svg` | Modo colapsable estrecho (72px) que mantiene visibles los iconos de navegación sin ocultar la barra de la pantalla. |

Las ventanas de video se abren en el equipo donde se ejecuta Streamlit. Si se accede al panel desde otro equipo, allí solo se verán los controles y las métricas. La demostración y el análisis en vivo usan la cámara por turnos.

```
┌─────────────────────────────────────────────────────────────────┐
│                 VIGILANTE EPP 4.0 — Dashboard                   │
├───────────────────┬─────────────────────────────────────────────┤
│  Navegación       │  Vista Activa                               │
│  ──────────       │  ────────────                               │
│  [■] Demostración │  [MODO SELECCIONADO]                        │
│  [■] Análisis Vivo│  Telemetría · Detección YOLOv8              │
│  [■] Estadísticas │  Control SPC · Gráficos · Calculadora ROI   │
│  [■] Reportes     │  Bitácora Forense · Informes HTML / CSV     │
│  ──────────────── │                                             │
│  [⚙] Configuración│  Modal Compacto: 2 Columnas · Sin Scroll    │
│  [«] Contraer Riel│  Alterna barra entre 250px y 72px (Icon-only│
└───────────────────┴─────────────────────────────────────────────┘
```

---

## Características Principales

- **Detección en Tiempo Real** — YOLOv8 corriendo directamente en CPU/GPU local, sin depender de APIs externas.
- **Multi-Object Tracking (MOT)** — ByteTrack asigna IDs persistentes a cada operario entre frames para evitar registros duplicados.
- **Análisis Espacial por Trabajador** — El sistema agrupa detecciones de EPP por persona usando solapamiento geométrico, evaluando casco y chaleco de forma individual por operario.
- **Semáforo de Estado Inteligente** — Estado visual inmediato: `SEGURO (verde)` / `ADVERTENCIA (naranja)` / `INFRACCIÓN CRÍTICA (rojo)`.
- **Evidencia Fotográfica Automática** — Captura y guarda automáticamente JPGs de cada infracción detectada para trazabilidad legal.
- **Base de Datos Normalizada** — SQLite con esquema relacional (sesiones + eventos), índices B-Tree y soporte para múltiples turnos históricos.
- **Informes Forenses HTML** — Reportes auto-contenidos listos para guardar como PDF (ISO 45001 / OSHA 1910).
- **Calculadora de ROI** — Estimación interactiva de ahorro anual en multas y pólizas de seguro.
- **Modo Oscuro / Claro** — Interfaz adaptable con tema profesional.
- **100% Offline** — Funciona sin conexión a internet una vez instalado.

---

## Stack Tecnológico

| Componente | Tecnología | Versión |
|---|---|---|
| Lenguaje | Python | 3.9+ |
| Frontend / Web App | Streamlit | ≥ 1.50 |
| Detección IA | Ultralytics YOLOv8 | ≥ 8.1 |
| Multi-Object Tracking | ByteTrack (integrado en YOLO) | — |
| Procesamiento de Imagen | OpenCV (`cv2`) | ≥ 4.8 |
| Visualización Interactiva | Plotly | ≥ 5.0 |
| Base de Datos | SQLite (normalizada, multi-sesión) | built-in |
| Análisis de Datos | Pandas | ≥ 2.0 |
| Computación Numérica | NumPy | ≥ 1.24 |
| **Estilos** | CSS personalizado (`styles/styles.py`) | Tema Dark/Light con variables CSS semánticas, tipografía JetBrains Mono para telemetría, logo SVG vectorial en sidebar y header |

---

## Estructura del Proyecto

```
vigilante-epp/
│
├── README.md                       # Documentación principal del proyecto
├── PROJECT_MAP.md                  # Mapa integral de arquitectura y contexto técnico
├── LICENSE                         # Licencia MIT
├── requirements.txt                # Dependencias Python (Streamlit, YOLOv8, Plotly, etc.)
├── .gitignore                      # Exclusiones de Git (BD local, capturas, temporales)
├── .gitattributes                  # Normalización de saltos de línea (CRLF para .bat)
├── app.py                          # Aplicación principal Streamlit (navegación en sidebar y modal de configuración)
│
├── scripts/                        # Herramientas de ejecución multiplataforma
│   ├── 1_instalar.bat              # Instala todas las dependencias automáticamente (Windows)
│   ├── 1_instalar_linux.sh         # Instalación ligera optimizada PyTorch CPU (Linux)
│   ├── 2_iniciar.bat               # Lanza la aplicación en el navegador (Windows)
│   ├── 3_apagar.bat                # Cierra el servidor y libera la cámara (Windows)
│   ├── 4_publicar_github.bat       # Sincroniza cambios con GitHub con validación de seguridad (Windows)
│   └── 5_actualizar.bat            # Sincroniza y descarga últimos cambios con Git pull (Windows)
│
├── docs/                           # Documentación técnica y de proyecto
│   ├── DESIGN.md                   # Sistema de diseño sobrio industrial
│   └── proyecto_base.md            # Especificación base y guía de pitch (feria)
│
├── assets/
│   ├── logo.jpg                    # Logo del sistema (fallback)
│   ├── logo.svg                    # Logo vectorial principal en Base64
│   └── *.svg                       # Catálogo de iconos vectoriales SVG locales (navegación, telemetría y reportes)
│
├── models/
│   └── ppe_model.pt                # Modelo YOLOv8 especializado en EPP (~6.2 MB)
│
├── modules/                        # Arquitectura modular del backend
│   ├── __init__.py
│   ├── audit_writer.py             # Persistencia asíncrona desacoplada en SQLite y evidencias en disco
│   ├── auditor_core.py             # Núcleo base común de inferencia (BaseAuditorService) y renderizado BGR
│   ├── auditor.py                  # Servicio de auditoría en vivo (LiveAuditorService) conectado a SQLite
│   ├── camera.py                   # Captura multihilo desacoplada, buffer O(1) y gestión singleton de hardware
│   ├── camera_sources.py           # Centralización de fuentes de cámara y exclusión mutua de hardware
│   ├── charts.py                   # Gráficos SPC (Shewhart Run Chart) y severidad con Plotly
│   ├── database.py                 # Capa SQLite WAL optimizada con incrementos atómicos y consultas agregadas
│   ├── demo_video.py               # Servicio de demostración en memoria (cero persistencia en BD)
│   ├── detector.py                 # Inferencia YOLOv8 BGR nativo, tracking y análisis espacial
│   ├── metrics.py                  # Inicialización de estado y cálculo interactivo de ROI
│   ├── native_viewer.py            # Visor OpenCV en hilo Win32 dedicado con repintado continuo a 50 FPS
│   ├── report_generator.py         # Generador de informes HTML forenses (exportables a PDF)
│   ├── samples.py                  # Generador de escenarios sintéticos de demo
│   ├── tracker_manager.py          # Anti-duplicación y cooldown por operario (MOT)
│   └── views/                      # Vistas modulares de la interfaz Streamlit
│       ├── __init__.py             # Exportaciones de vistas
│       ├── components.py           # Componentes visuales reutilizables y presets
│       ├── config_dialog.py        # Diálogo modal emergente (@st.dialog)
│       ├── demo_view.py            # Vista de sandbox de demostración
│       ├── live_view.py            # Vista de supervisión en vivo
│       ├── stats_view.py           # Vista de estadísticas, SPC y ROI
│       └── reports_view.py         # Vista de dictamen pericial, bitácora y exportación
│
├── tests/                          # Suite formal de pruebas automatizadas (39 pruebas unitarias al 100% OK)
│   ├── test_app_navigation.py      # Pruebas de navegación y estado en Streamlit
│   ├── test_audit_writer.py        # Pruebas de cola asíncrona de auditoría
│   ├── test_auditor_first_frame.py # Pruebas de primera previsualización y visor nativo
│   ├── test_camera_frame_sequence.py # Pruebas de integridad de fotogramas de cámara
│   ├── test_camera_sources.py      # Pruebas de escaneo dinámico y normalización de URLs
│   └── test_demo_video.py          # Pruebas de demostración en memoria sin persistencia
│
├── styles/                         # Componentes visuales y CSS
│   ├── __init__.py
│   ├── icons.py                    # Gestor de iconos vectoriales SVG locales y proveedor de data-URIs
│   └── styles.py                   # Temas (Dark/Light Cockpit), header, cards, riel permanente y botones minimalistas
│
└── .streamlit/
    └── config.toml                 # Tema visual de Streamlit
```

> **Nota:** Las carpetas `data/` (base de datos SQLite) y `captures/` (evidencias fotográficas) se generan automáticamente al ejecutar la app y están excluidas del repositorio por privacidad.

---

## Instalación y Ejecución

### Prerequisitos
- Python 3.9 o superior
- Webcam (para el modo de monitoreo en vivo)

### Opción A — Scripts automáticos (Windows, recomendado)

Dentro de la carpeta `scripts/` encontrarás todo lo que necesitas, en orden:

| Script | Acción |
|---|---|
| `scripts/1_instalar.bat` | Instala todas las dependencias automáticamente (Windows) |
| `scripts/1_instalar_linux.sh` | Instalación ligera con PyTorch CPU optimizado (Linux) |
| `scripts/2_iniciar.bat` | Lanza la app en el navegador |
| `scripts/3_apagar.bat` | Cierra el servidor y libera la cámara |
| `scripts/4_publicar_github.bat` | Sube tus cambios a GitHub con verificación de seguridad |
| `scripts/5_actualizar.bat` | Sincroniza y descarga las últimas actualizaciones de GitHub |

> Doble clic sobre cada `.bat` para ejecutarlo en Windows (o `bash scripts/1_instalar_linux.sh` en Linux).

### Opción B — Manual (cualquier sistema operativo)

**1. Clonar el repositorio**
```bash
git clone https://github.com/tu-usuario/vigilante-epp.git
cd vigilante-epp
```

**2. Crear entorno virtual (recomendado)**
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

**3. Instalar dependencias**
```bash
pip install -r requirements.txt
```

**4. Ejecutar la aplicación**
```bash
streamlit run app.py
```

La aplicación abrirá automáticamente en tu navegador en **`http://localhost:8501`**.

### Soporte de Exportación Directa a PDF

El módulo de Reportes soporta exportación directa a documentos PDF mediante la librería `weasyprint>=60.0` (incluida en `requirements.txt`).

- **Degradación automática:** Si las dependencias del sistema no se encuentran disponibles, la aplicación conmuta automáticamente a la descarga del informe en formato HTML con activación automática de impresión (`window.print()`), garantizando la disponibilidad del dictamen sin intervención del usuario.
- **Dependencias en Windows:** En entornos Windows, WeasyPrint requiere las librerías GTK3 (`libgobject-2.0-0` y asociadas). Para habilitar la generación directa de archivos PDF en este sistema operativo, consulte la documentación oficial de referencia: [Instalación de dependencias GTK para WeasyPrint](https://weasyprint.readthedocs.io/en/stable/first_steps/installation.html).

---

## Cómo Funciona

```
Entrada de Video
  (Webcam / RTSP / Foto)
        │
        ▼
┌──────────────────┐
│  YOLOv8 + BYTE   │  ← Detección de objetos + IDs persistentes por persona
│  TRACK (MOT)     │
└────────┬─────────┘
         │ detections_list[]
         ▼
┌──────────────────┐
│ Análisis Espacial│  ← Agrupa casco/chaleco por trabajador via solapamiento
│ por Trabajador   │    geométrico de bounding boxes
└────────┬─────────┘
         │ workers_list[]
         ▼
┌──────────────────┐
│ WorkerTrackMgr   │  ← Anti-spam: cooldown individual por ID de operario
│ (Deduplicación)  │    Requiere 2 frames consecutivos para confirmar infracción
└────────┬─────────┘
         │ should_record = True/False
         ▼
┌──────────────────┐
│  SQLite DB       │  ← Registra evento en tabla normalizada (sesión + operario)
│  + JPG Evidencia │    Guarda foto de la infracción automáticamente
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Dashboard HUD   │  ← Semáforo, KPIs, últimas auditorías, gráficos
│  Streamlit UI    │    Informe HTML exportable
└──────────────────┘
```

---

## Módulos del Sistema

### `modules/auditor.py`
Servicio de auditoría formal desacoplado en segundo plano (`LiveAuditorService`). Ejecuta un hilo demonio independiente de la UI de Streamlit que orquesta la inferencia continua, tracking MOT, evaluación espacial de EPP y entrega de telemetría en tiempo constante O(1).

### `modules/demo_video.py`
Servicio de demostración interactiva en memoria (`DemoVideoService`). Réplica exacta de la experiencia visual de Análisis en Vivo (tracking MOT, cajas de operario, banner superior HUD) pero con **cero persistencia en SQLite y cero capturas en disco**. Mantiene incidentes recientes y KPIs en RAM volátil (`collections.deque(maxlen=6)`). Soporta tanto video continuo como fotos subidas y escenarios sintéticos.

### `modules/native_viewer.py`
Visor nativo de escritorio OpenCV (`LatestFrameNativeViewer`) con un único hilo propietario Win32 (`NativeViewerOwner`). Implementa entrega en tiempo constante O(1) del último fotograma y repintado continuo a ~50 FPS (`waitKey(20)`), evitando congelamientos y pantallas grises durante el warmup inicial de YOLO.

### `modules/audit_writer.py`
Cola de persistencia transaccional asíncrona (`AuditEventWriter`). Procesa en segundo plano la escritura de eventos en SQLite y la compresión/almacenamiento de evidencias JPG, blindando el motor de visión para mantener una tasa de FPS estable sin latencias de disco.

### `modules/camera_sources.py`
Controlador centralizado de fuentes de captura y exclusión mutua de hardware (`CAMERA_MODE_LOCK`). Resuelve selectores de dispositivos (cámaras integradas, USB o RTSP) y garantiza una alternancia limpia entre Demostración y Análisis en Vivo sin colisiones en Windows DirectShow.

### `modules/camera.py`
Captura de video multihilo desacoplada (`ThreadedCamera` y `CameraStreamManager`) con backend DirectShow en Windows y buffer O(1). Mantiene el stream vivo en segundo plano de forma independiente a los re-renders de Streamlit.

### `modules/detector.py`
Motor principal de visión artificial. Soporta inferencia estándar y tracking persistente (ByteTrack). Incluye análisis espacial para asignar detecciones de EPP a cada persona individualmente.

### `modules/tracker_manager.py`
Capa de lógica anti-duplicación (`WorkerTrackManager`). Aplica cooldowns individuales por ID de operario (45 s infracciones), requiere 2 frames consecutivos para confirmar una alerta (anti-parpadeo) y purga pistas inactivas.

### `modules/database.py`
Esquema relacional SQLite de dos tablas (`camera_sessions` + `camera_events`) con claves foráneas, índices B-Tree y modo concurrente WAL (`PRAGMA journal_mode = WAL`).

### `modules/charts.py`
Gráficos interactivos de Control Estadístico de Procesos (SPC / Shewhart Run Chart) y distribución de severidad cromática con Plotly bajo normativas ISO 45001 / OSHA 1910.

### `modules/report_generator.py`
Genera informes HTML auto-contenidos con membrete corporativo, galería de evidencias fotográficas en Base64, tabla forense y casillas de firma — listos para imprimir como PDF.

### `modules/metrics.py`
Capa de sesión Streamlit y analítica ejecutiva. Conecta el estado de `st.session_state` con la base de datos, calcula el ROI de multas y expone wrappers limpios para la UI.

### `tests/`
Suite formal de pruebas automatizadas compuestas por 31 pruebas unitarias (`test_demo_video.py`, `test_auditor_first_frame.py`, `test_audit_writer.py`, `test_app_navigation.py`, `test_camera_frame_sequence.py`) que validan la entrega de previsualización, tracking, persistencia y navegación con 100% de éxito.

---

## Impacto y ROI

| Indicador | Valor Proyectado |
|---|---|
| Reducción de infracciones de EPP | **~85%** |
| Infracciones prevenidas / 100 trabajadores / año | **~30** |
| Ahorro estimado en multas y pólizas (100 trabajadores) | **~$75,000 USD/año** |
| Tiempo de respuesta ante infracción | **< 2 segundos** |
| Disponibilidad del sistema | **24/7 sin fatiga** |

> Calcula el ahorro específico para tu empresa en la sección **▲ Estadísticas** de la aplicación.

---

## Roadmap

- [x] Detección en tiempo real (YOLOv8)
- [x] Multi-Object Tracking (ByteTrack)
- [x] Base de datos multi-sesión (SQLite)
- [x] Informes HTML exportables (ISO 45001)
- [x] Calculadora interactiva de ROI
- [ ] Soporte para detección de guantes y gafas de seguridad
- [ ] Notificaciones por correo / SMS ante infracciones críticas
- [ ] Panel web multi-cámara con mapa de planta
- [ ] API REST para integración con sistemas SCADA/ERP
- [x] Exportación de informes en PDF nativo (con degradación automática a HTML)

---

## Contribuir

Las contribuciones son bienvenidas. Para contribuir:

1. Haz un **Fork** del repositorio
2. Crea una rama para tu feature: `git checkout -b feature/nueva-funcionalidad`
3. Realiza tus cambios y haz commit: `git commit -m 'feat: descripción del cambio'`
4. Sube la rama: `git push origin feature/nueva-funcionalidad`
5. Abre un **Pull Request**

---

## Licencia

Este proyecto está bajo la Licencia **MIT**. Consulta el archivo [LICENSE](LICENSE) para más detalles.

---

<div align="center">

Desarrollado para la **Feria de Proyectos de Emprendimiento 2026**

*Prevención Proactiva de Accidentes Laborales · Inteligencia Artificial Aplicada a la Seguridad Industrial*

</div>
