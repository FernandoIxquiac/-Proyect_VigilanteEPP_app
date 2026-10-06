# 🛡️ Vigilante EPP — SafeGuard AI

<div align="center">

**Sistema Inteligente de Detección de Equipos de Protección Personal en Tiempo Real**

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776ab?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-ff4b4b?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-00C4CC?style=for-the-badge&logo=yolo&logoColor=white)](https://ultralytics.com)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8%2B-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)](https://opencv.org/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://www.sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](LICENSE)

*Prevención proactiva de accidentes laborales con Inteligencia Artificial · Feria de Proyectos 2026*

</div>

---

## 📋 Tabla de Contenidos

- [¿Qué es Vigilante EPP?](#-qué-es-vigilante-epp)
- [Demostración](#-demostración)
- [Características Principales](#-características-principales)
- [Stack Tecnológico](#-stack-tecnológico)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Instalación y Ejecución](#-instalación-y-ejecución)
- [Cómo Funciona](#-cómo-funciona)
- [Módulos del Sistema](#-módulos-del-sistema)
- [Impacto y ROI](#-impacto-y-roi)
- [Contribuir](#-contribuir)
- [Licencia](#-licencia)

---

## 🔍 ¿Qué es Vigilante EPP?

**Vigilante EPP** es una plataforma de visión por computadora que analiza transmisiones de video en tiempo real para detectar automáticamente la **presencia o ausencia de Equipos de Protección Personal (EPP)** — casco de seguridad y chaleco reflectante — en entornos industriales.

> **Problema Real:** En sectores como minería, manufactura y construcción, más del **40% de los accidentes graves** ocurren por falta de uso o uso indebido de EPP. La supervisión humana tradicional es intermitente, costosa y propensa al error.

> **Nuestra Solución:** Monitoreo continuo con IA, alertas visuales inmediatas, trazabilidad por operario y generación automática de informes forenses — sin necesidad de servidores externos ni infraestructura costosa.

---

## 🎬 Demostración

| Pestaña | Descripción |
|---|---|
| **📹 Live View** | Monitoreo en vivo con webcam o flujo RTSP/IP. Detección frame a frame con tracking persistente (ByteTrack MOT). |
| **🖼️ Audit** | Análisis forense de fotografías de planta. Comparador visual lado a lado original vs. IA. |
| **📊 ROI & Métricas** | Panel gerencial con KPIs, gráficos de tendencia, calculadora interactiva de ahorro y exportación de informes HTML/CSV. |

```
┌─────────────────────────────────────────────────────────────────┐
│                 🛡️ VIGILANTE EPP 4.0 — Dashboard                │
├──────────────────┬──────────────────────┬───────────────────────┤
│  📹 Live View    │  🖼️ Audit            │  📊 ROI & Métricas    │
│                  │                      │                       │
│  [CAM] ──► IA   │  [FOTO] ──► Análisis │  KPIs · Gráficos      │
│  Semáforo HUD    │  Tabla de desglose   │  ROI Calculator       │
│  Tracker MOT     │  por trabajador      │  Exportar HTML/CSV    │
└──────────────────┴──────────────────────┴───────────────────────┘
```

---

## ✨ Características Principales

- **🎯 Detección en Tiempo Real** — YOLOv8 corriendo directamente en CPU/GPU local, sin depender de APIs externas.
- **👤 Multi-Object Tracking (MOT)** — ByteTrack asigna IDs persistentes a cada operario entre frames para evitar registros duplicados.
- **🧠 Análisis Espacial por Trabajador** — El sistema agrupa detecciones de EPP por persona usando solapamiento geométrico, evaluando casco y chaleco de forma individual por operario.
- **🚦 Semáforo de Estado Inteligente** — Estado visual inmediato: `SEGURO (verde)` / `ADVERTENCIA (naranja)` / `INFRACCIÓN CRÍTICA (rojo)`.
- **📸 Evidencia Fotográfica Automática** — Captura y guarda automáticamente JPGs de cada infracción detectada para trazabilidad legal.
- **🗄️ Base de Datos Normalizada** — SQLite con esquema relacional (sesiones + eventos), índices B-Tree y soporte para múltiples turnos históricos.
- **📑 Informes Forenses HTML** — Reportes auto-contenidos listos para guardar como PDF (ISO 45001 / OSHA 1910).
- **💰 Calculadora de ROI** — Estimación interactiva de ahorro anual en multas y pólizas de seguro.
- **🌓 Modo Oscuro / Claro** — Interfaz adaptable con tema profesional.
- **📴 100% Offline** — Funciona sin conexión a internet una vez instalado.

---

## 🧱 Stack Tecnológico

| Componente | Tecnología | Versión |
|---|---|---|
| Lenguaje | Python | 3.9+ |
| Frontend / Web App | Streamlit | ≥ 1.30 |
| Detección IA | Ultralytics YOLOv8 | ≥ 8.1 |
| Multi-Object Tracking | ByteTrack (integrado en YOLO) | — |
| Procesamiento de Imagen | OpenCV (`cv2`) | ≥ 4.8 |
| Visualización Interactiva | Plotly | ≥ 5.0 |
| Base de Datos | SQLite (normalizada, multi-sesión) | built-in |
| Análisis de Datos | Pandas | ≥ 2.0 |
| Computación Numérica | NumPy | ≥ 1.24 |

---

## 📁 Estructura del Proyecto

```
vigilante-epp/
│
├── 📄 README.md                    # Documentación principal del proyecto
├── 🗺️ PROJECT_MAP.md              # Mapa integral de arquitectura y contexto técnico
├── 📄 LICENSE                      # Licencia MIT
├── 📄 requirements.txt             # Dependencias Python (Streamlit, YOLOv8, Plotly, etc.)
├── 📄 .gitignore                   # Exclusiones de Git (BD local, capturas, temporales)
├── 📄 .gitattributes              # Normalización de saltos de línea (CRLF para .bat)
├── 🐍 app.py                       # Aplicación principal Streamlit (3 pestañas)
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
│   └── proyecto_base.md            # Especificación base y guía de pitch (feria)
│
├── assets/
│   └── logo.jpg                    # Logo del sistema
│
├── models/
│   └── ppe_model.pt                # Modelo YOLOv8 especializado en EPP (~6.2 MB)
│
├── modules/                        # Arquitectura modular del backend
│   ├── __init__.py
│   ├── camera.py                   # Captura multihilo desacoplada, buffer O(1) y gestión de hardware
│   ├── detector.py                 # Inferencia YOLO, tracking y análisis espacial
│   ├── tracker_manager.py          # Anti-duplicación y cooldown por operario (MOT)
│   ├── database.py                 # Esquema SQLite, CRUD, sesiones y consultas
│   ├── metrics.py                  # Capa de sesión Streamlit + analítica y ROI
│   ├── charts.py                   # Gráficos SPC (Shewhart Run Chart) y severidad con Plotly
│   ├── report_generator.py         # Generador de informes HTML forenses (exportables a PDF)
│   └── samples.py                  # Generador de escenarios sintéticos de demo
│
├── styles/                         # Componentes visuales y CSS
│   ├── __init__.py
│   └── styles.py                   # Temas (Dark/Light Cockpit), header, cards de estado e incidentes
│
└── .streamlit/
    └── config.toml                 # Tema visual de Streamlit
```

> **Nota:** Las carpetas `data/` (base de datos SQLite) y `captures/` (evidencias fotográficas) se generan automáticamente al ejecutar la app y están excluidas del repositorio por privacidad.

---

## ⚡ Instalación y Ejecución

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

---

## ⚙️ Cómo Funciona

```
Entrada de Video
  (Webcam / RTSP / Foto)
        │
        ▼
┌──────────────────┐
│  YOLOv8 + BYTE  │  ← Detección de objetos + IDs persistentes por persona
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

## 🧩 Módulos del Sistema

### `modules/camera.py`
Captura de video multihilo desacoplada con backend DirectShow en Windows y buffer O(1). Mantiene el stream vivo en segundo plano de forma independiente a los re-renders de Streamlit.

### `modules/detector.py`
Motor principal de visión artificial. Soporta inferencia estándar y tracking persistente (ByteTrack). Incluye análisis espacial para asignar detecciones de EPP a cada persona individualmente.

### `modules/tracker_manager.py`
Capa de lógica anti-duplicación. Aplica cooldowns individuales por ID de operario (60 s infracciones, 120 s cumplimiento), requiere 2 frames consecutivos para confirmar una alerta y detecta cuándo un operario subsana su infracción.

### `modules/database.py`
Esquema relacional SQLite de dos tablas (`camera_sessions` + `camera_events`) con claves foráneas, índices B-Tree y migraciones automáticas seguras. Gestiona múltiples turnos sin borrar historial.

### `modules/charts.py`
Gráficos interactivos de Control Estadístico de Procesos (SPC / Shewhart Run Chart) y distribución de severidad cromática con Plotly bajo normativas ISO 45001 / OSHA 1910.

### `modules/report_generator.py`
Genera informes HTML auto-contenidos con membrete corporativo, galería de evidencias fotográficas en Base64, tabla forense y casillas de firma — listos para imprimir como PDF.

### `modules/metrics.py`
Capa de sesión Streamlit y analítica ejecutiva. Conecta el estado de `st.session_state` con la base de datos, calcula el ROI de multas y expone wrappers limpios para la UI.

---

## 💰 Impacto y ROI

| Indicador | Valor Proyectado |
|---|---|
| Reducción de infracciones de EPP | **~85%** |
| Infracciones prevenidas / 100 trabajadores / año | **~30** |
| Ahorro estimado en multas y pólizas (100 trabajadores) | **~\$75,000 USD/año** |
| Tiempo de respuesta ante infracción | **< 2 segundos** |
| Disponibilidad del sistema | **24/7 sin fatiga** |

> Calcula el ahorro específico para tu empresa en la pestaña **📊 ROI & Métricas** de la aplicación.

---

## 🗺️ Roadmap

- [x] Detección en tiempo real (YOLOv8)
- [x] Multi-Object Tracking (ByteTrack)
- [x] Base de datos multi-sesión (SQLite)
- [x] Informes HTML exportables (ISO 45001)
- [x] Calculadora interactiva de ROI
- [ ] Soporte para detección de guantes y gafas de seguridad
- [ ] Notificaciones por correo / SMS ante infracciones críticas
- [ ] Panel web multi-cámara con mapa de planta
- [ ] API REST para integración con sistemas SCADA/ERP
- [ ] Exportación de informes en PDF nativo (sin Ctrl+P)

---

## 🤝 Contribuir

Las contribuciones son bienvenidas. Para contribuir:

1. Haz un **Fork** del repositorio
2. Crea una rama para tu feature: `git checkout -b feature/nueva-funcionalidad`
3. Realiza tus cambios y haz commit: `git commit -m 'feat: descripción del cambio'`
4. Sube la rama: `git push origin feature/nueva-funcionalidad`
5. Abre un **Pull Request**

---

## 📄 Licencia

Este proyecto está bajo la Licencia **MIT**. Consulta el archivo [LICENSE](LICENSE) para más detalles.

---

<div align="center">

Desarrollado con ❤️ para la **Feria de Proyectos de Emprendimiento 2026**

*Prevención Proactiva de Accidentes Laborales · Inteligencia Artificial Aplicada a la Seguridad Industrial*

</div>
