# DESIGN SYSTEM — Vigilante EPP (SafeGuard AI 4.0)

> **Documento Maestro de Identidad Visual, UI/UX y Estándares de Interfaz**  
> **Enfoque:** Sobrio, Corporativo, Intuitivo y de Alta Legibilidad Operativa  
> **Normativas de Referencia:** ISO 3864 (Colores de Seguridad), ISO 45001, OSHA 1910  

---

## Tabla de Contenidos
1. [Filosofía de Diseño y Principios UX](#1-filosofía-de-diseño-y-principios-ux)
2. [Identidad de Marca y Uso del Logotipo](#2-identidad-de-marca-y-uso-del-logotipo)
3. [Sistema de Color (UI, OpenCV, Plotly e Impresión)](#3-sistema-de-color-ui-opencv-plotly-e-impresión)
4. [Tipografía y Jerarquía Visual](#4-tipografía-y-jerarquía-visual)
5. [Nuevo Layout y Arquitectura de Interfaz](#5-nuevo-layout-y-arquitectura-de-interfaz)
6. [Revisiones y Decisiones de Diseño (Changelog)](#6-revisiones-y-decisiones-de-diseño-changelog)
7. [Clases Utilitarias CSS y Componentes UI (`styles/styles.py`)](#7-clases-utilitarias-css-y-componentes-ui-stylesstylespy)
8. [Estándar de Visión Artificial BGR y Núcleo de Inferencia (`modules/auditor_core.py`)](#8-estándar-de-visión-artificial-bgr-y-núcleo-de-inferencia-modulesauditor_corepy)
9. [Reglas Anti-Slop, Prohibición de Emojis y Código Limpio](#9-reglas-anti-slop-prohibición-de-emojis-y-código-limpio)

---

## 1. Filosofía de Diseño y Principios UX

El rediseño de **Vigilante EPP** abandona los efectos recargados o experimentales para adoptar una estética **Enterprise Industrial Sobria**: limpia, ordenada, predecible y sin fricción visual.

### Los 4 Pilares de la Interfaz
1. **Sobriedad Operativa (Zero Visual Noise):** Los colores intensos (rojo, ámbar, verde, cian) **nunca** se usan como decoración de fondo; se reservan exclusivamente para comunicar estados reales del sistema o acciones primarias.
2. **Escaneabilidad en < 2 Segundos:** Un supervisor de planta debe mirar el monitor a 3 metros de distancia y saber instantáneamente si la zona está en estado **Seguro**, **Advertencia** o **Infracción Crítica**.
3. **Jerarquía Clara (F-Pattern Layout):** Información de estado arriba, flujo visual principal a la izquierda (70%) y telemetría/bitácora de incidentes a la derecha (30%), sin necesidad de hacer scroll vertical en la vista en vivo.
4. **Natividad Estética en Streamlit:** En lugar de pelear contra todos los contenedores internos de Streamlit con selectores frágiles, se delega el 80% de la tematización base a `.streamlit/config.toml` y variables CSS nativas, reservando `styles.py` para pulir estructura, tarjetas semánticas y bordes limpios.

---

## 2. Identidad de Marca y Uso del Logotipo

El logotipo de **Vigilante EPP** combina tres conceptos:
- **El Escudo Acero:** Protección física y robustez industrial.
- **El Obturador / Iris Óptico:** Visión por computadora continua y precisión analítica.
- **Las Pistas de Circuito:** Inteligencia Artificial ejecutándose localmente (Edge AI).

### Reglas de Aplicación
- **Archivo Principal en UI:** Usar preferentemente `assets/logo.svg` embebido en Base64 dentro del Header superior para garantizar nitidez vectorial en cualquier resolución (4K o 1080p) sin fondo blanco residual.
- **Archivo para Documentos/ Portadas:** Usar `assets/logo.jpg` en portadas de presentaciones o `logo.svg` en el membrete de informes forenses HTML.
- **Tamaños Mínimos:**
  - En el Header de la aplicación: `36px` a `42px` de alto.
  - En informes HTML/PDF: `48px` de alto.
- **Área de Resguardo:** Mantener un margen libre mínimo de `8px` alrededor del escudo sin bordes ni textos pegados.

---

## 3. Sistema de Color (UI, OpenCV, Plotly e Impresión)

La paleta nace directamente de los pigmentos del logotipo (`logo.svg`) y se adapta a la normativa internacional de señalización industrial **ISO 3864**.

### 3.1 Colores de Marca (Extraídos del Logo)
| Token | Nombre | HEX | RGB | Uso Principal |
| :--- | :--- | :---: | :---: | :--- |
| `--brand-navy` | **Azul Marino Abisal** | `#07162C` | `7, 22, 44` | Fondo principal (Dark Mode) y textos de marca en claro |
| `--brand-cyan` | **Cian Óptico (Primary)** | `#00A8E8` | `0, 168, 232` | Color de acento primario, pestaña activa, foco e iconos |
| `--brand-blue` | **Azul Cobalto Corporativo**| `#0284C7` | `2, 132, 199` | Acento primario en Modo Claro (mayor contraste sobre blanco) |
| `--brand-steel`| **Acero Titanio** | `#94A3B8` | `148, 163, 184`| Bordes metálicos, iconos secundarios y textos de soporte |

### 3.2 Superficies y Neutros (Modo Oscuro vs. Modo Claro)

| Rol de Superficie | Token CSS | Modo Oscuro (Por Defecto) | Modo Claro (Ejecutivo/Impresión) |
| :--- | :--- | :---: | :---: |
| **Fondo de Aplicación** | `--bg-app` | `#0B111E` (Pizarra Nocturna) | `#F4F6F9` (Gris Técnico Hielo) |
| **Fondo de Sidebar / Paneles**| `--bg-panel` | `#111827` (Gris Carbón Azul) | `#FFFFFF` (Blanco Puro) |
| **Fondo de Tarjetas (Cards)** | `--bg-card` | `#161F30` (Superficie Elevada) | `#FFFFFF` (Blanco Puro) |
| **Fondo de Inputs / Hover** | `--bg-elevated`| `#1E293B` (Slate 800) | `#F8FAFC` (Slate 50) |
| **Borde Sutil de Contenedor** | `--border-subtle`| `#26334D` | `#E2E8F0` |
| **Borde Fuerte / Separador** | `--border-strong`| `#334155` | `#CBD5E1` |
| **Texto Principal** | `--text-primary`| `#F8FAFC` | `#0F172A` |
| **Texto Secundario / Labels** | `--text-secondary`| `#CBD5E1` | `#475569` |
| **Texto Deshabilitado / Muted**| `--text-muted` | `#94A3B8` | `#94A3B8` |

### 3.3 Colores Semánticos de Seguridad (Semáforo HUD + OpenCV)
> **Nota técnica para OpenCV (`detector.py`):** OpenCV utiliza el orden **BGR** `(Azul, Verde, Rojo)` en lugar de RGB. Usa siempre la columna **Tupla BGR** en tu código Python de visión artificial.

| Estado del Sistema | HEX (UI / Plotly) | Fondo Suave (Badge UI) | Borde (Badge UI) | Tupla BGR (OpenCV) | Cuándo se activa |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **SEGURO (`safe`)** | `#10B981` | `rgba(16, 185, 129, 0.12)` | `rgba(16, 185, 129, 0.35)` | `(129, 185, 16)` | Operario con Casco **Y** Chaleco completos |
| **ADVERTENCIA (`warning`)**| `#F59E0B` | `rgba(245, 158, 11, 0.12)` | `rgba(245, 158, 11, 0.35)` | `(11, 158, 245)` | Uso parcial (falta 1 EPP) o baja confianza |
| **CRÍTICO (`danger`)** | `#EF4444` | `rgba(239, 68, 68, 0.14)` | `rgba(239, 68, 68, 0.40)` | `(68, 68, 239)` | Operario sin EPP en zona activa (Infracción) |
| **EN ESPERA (`standby`)** | `#00A8E8` | `rgba(0, 168, 232, 0.12)` | `rgba(0, 168, 232, 0.35)` | `(232, 168, 0)` | Cámara en espera o escena sin personal (`0`) |

---

## 4. Tipografía y Jerarquía Visual

Para lograr una apariencia sobria, técnica y sumamente legible sin sobrecargar el navegador, se utilizan **2 familias tipográficas de Google Fonts**:

1. **`Inter` (UI & Lectura General):** Limpia, neutra y estándar en interfaces empresariales modernas.
2. **`JetBrains Mono` (Telemetría, IDs, Timestamps y KPIs):** Fuente monoespaciada técnica que evita que los números "bailen" cuando cambian en tiempo real frame a frame.

### Escala Tipográfica
| Elemento | Fuente | Tamaño (`rem`/`px`) | Peso (`font-weight`) | Estilo Adicional |
| :--- | :--- | :---: | :---: | :--- |
| **Título de Marca (Header)** | `Inter` | `1.05rem` (`16.8px`) | `800` (ExtraBold) | `letter-spacing: 0.04em`, `UPPERCASE` |
| **Encabezado de Sección (H2/H3)**| `Inter` | `0.95rem` (`15.2px`) | `700` (Bold) | `letter-spacing: -0.01em` |
| **Valor de KPI (`stMetricValue`)**| `JetBrains Mono`| `1.35rem` (`21.6px`) | `700` (Bold) | `font-variant-numeric: tabular-nums` |
| **Etiqueta de KPI (`stMetricLabel`)**| `Inter` | `0.70rem` (`11.2px`) | `600` (SemiBold) | `UPPERCASE`, `letter-spacing: 0.05em` |
| **Cuerpo de Texto / Controles** | `Inter` | `0.85rem` (`13.6px`) | `400` / `500` | `line-height: 1.45` |
| **Timestamps / IDs (`#ID-04`)** | `JetBrains Mono`| `0.72rem` (`11.5px`) | `600` (SemiBold) | Ideal para tarjetas de incidentes y tablas |

---

## 5. Nuevo Layout y Arquitectura de Interfaz

El nuevo diseño organiza la pantalla en un **Grid Ejecutivo de Vista Única (Single-Viewport Cockpit)** de hasta `1280px` de ancho máximo, eliminando espacios muertos superiores y separando claramente **Configuración** (Sidebar), **Operación** (Centro) y **Evidencia/Estado** (Derecha).

### 5.1 Diagrama Estructural del Nuevo Layout

```text
┌───────────────────┬──────────────────────────────────────────────────────────────────────┐
│ SIDEBAR (260px)   │ HEADER INSTITUCIONAL COMPACTO (52px alto)                            │
│ (Colapsable)      │ [Logo SVG] VIGILANTE EPP 4.0 | SafeGuard AI      [● ONLINE] [YOLOv8] │
│                   ├──────────────────────────────────────────────────────────────────────┤
│ ⚙ Configuracion   │ VISTA ACTIVA: [ ◈ Demostracion | ◉ Analisis Vivo | ▲ Estadisticas | ≡ Reportes ]│
│ - Tema Oscuro/Claro──────────────────────────────────────────────┬───────────────────────┤
│ - Umbral Confianza│                                              │ ● ESTADO DE PLANTA    │
│ - Cámara / RTSP   │          VISOR DE VIDEO / CÁMARA             │ [ Tarjeta Semáforo ]  │
│                   │             (Columna 70% - Ratio 16:9)       │                       │
│ Controles         │                                              ├───────────────────────┤
│ [Iniciar]         │      • Borde sobrio de 1px                   │ RESUMEN DE TURNO      │
│ [Detener]         │      • Altura controlada (max 440px)         │ ┌─────────┬─────────┐ │
│                   │      • Centrado automático                   │ │En Escena│Cumplim.%│ │
│ Apariencia        │                                              │ └─────────┴─────────┘ │
│ [ Toggle Tema ]   ├──────────────┬───────────────┬───────────────┼───────────────────────┤
│                   │ KPI: Cascos  │ KPI: Chalecos │ KPI: Alertas  │ BITÁCORA EN VIVO      │
│ Info Sistema      │   98.2%      │    94.5%      │      02       │ • Op #04              │
│ DB: Conectada     │              │               │               │ • Op #02              │
└───────────────────┴──────────────┴───────────────┴───────────────┴───────────────────────┘
```

---

## 6. Revisiones y Decisiones de Diseño (Changelog)

### v4.1 — Ajustes de Accesibilidad y Coherencia Visual (2026-10-16)

#### 6.1 Logo en Sidebar vía Base64
- **Cambio:** El logo del sidebar ahora se carga desde `assets/logo.svg` embebido en Base64 (mismo mecanismo que el header superior), garantizando nitidez vectorial en cualquier resolución. Fallback automático a `assets/logo.jpg`.
- **Implementación:** `app.py` usa `_get_logo_base64()` de `styles.py` y renderiza con `st.markdown()` + HTML `<img>`.

#### 6.2 Bordes Uniformes (Sin Acento Lateral Asimétrico)
- **Cambio:** Se eliminaron los bordes laterales marcados (`border-left: 3px/4px solid`) del header, status card e incident card. Todos los bordes son ahora uniformes.
- **Razón:** El border-left asimétrico generaba ruido visual inconsistente con el principio de "Zero Visual Noise" del §1. La información de estado se comunica suficientemente a través del color del badge y el fondo de la tarjeta.
- **Aplicación:**
  - Header: `border: 1px solid var(--border-subtle)` (uniforme)
  - Status Card: `border: 2px solid {semantic-color}` (uniforme, color semántico)
  - Incident Card: `border: 1px solid {semantic-color-transparent}` (uniforme)

#### 6.3 Texto Secundario en Modo Oscuro — Mayor Contraste
- **Cambio:** `--text-secondary` en dark mode: `#94A3B8` → `#CBD5E1` (Slate-300).
  `--text-muted` en dark mode: `#64748B` → `#94A3B8` (Slate-400).
- **Razón:** El valor anterior `#94A3B8` sobre fondo `#111827` producía una relación de contraste ~3.5:1, por debajo del mínimo WCAG AA de 4.5:1 para texto pequeño. El nuevo valor `#CBD5E1` supera ese umbral.
- **Solo afecta Modo Oscuro.** Los valores de Modo Claro no se modificaron.

---

### v4.2 — Navegación Industrial, Riel Permanente y Refinamiento Semántico (2026-10-20)

#### 6.4 Navegación Minimalista por Botones (Ghost / Flat Navigation)
- **Cambio:** Se reemplazó el selector `st.radio` por botones individuales reactivos integrados con `st.session_state.current_page`.
- **Estilo Visual:** Se abandonaron las cajas grises con bordes duros.
  - *Inactivo:* Fondo transparente (`background: transparent`), sin bordes (`border: 1px solid transparent`), texto e icono en `var(--text-secondary)`.
  - *Hover:* Relleno sutil `var(--brand-primary-soft)` y color de acento `var(--brand-primary)`.
  - *Activo (`kind="primary"`):* Relleno plano corporativo `var(--brand-primary)`, texto e icono en blanco `#FFFFFF` con sombra sutil de elevación.
- **Herencia Cromática:** Se implementó `.stSidebar .stButton button p, .stSidebar .stButton button span { color: inherit !important; }`, garantizando que el texto y el icono cambien de color sincronizadamente en todos los estados.

#### 6.5 Iconografía Vectorial SVG Local con CSS Mask
- **Cambio:** Eliminación de glifos de texto Unicode en la barra de navegación en favor de iconos SVG locales vectoriales ubicados en `assets/` (`device-desktop.svg`, `video.svg`, `chart-bar.svg`, `file-text.svg`, `settings.svg`, `chevrons-left.svg`).
- **Implementación:** El módulo `styles/icons.py` proporciona `get_svg_data_uri(name)` codificado con `urllib.parse.quote()` y protegido con `@lru_cache`. El CSS aplica las máscaras vectoriales mediante `-webkit-mask` y `mask` con `background-color: currentColor;`, adaptándose automáticamente a la paleta del estado del botón sin llamadas a la red.

#### 6.6 Riel Lateral Permanente (72px / 250px)
- **Cambio:** Se inhabilitó el colapso nativo a 0px de Streamlit (`button[data-testid="stSidebarCollapseButton"]` y `div[data-testid="collapsedControl"]` con `display: none !important;`).
- **Comportamiento:** La barra lateral nunca desaparece de la pantalla. El usuario puede alternar entre:
  - *Modo Expandido:* Ancho de 250px con iconos alineados a la izquierda y etiquetas descriptivas legibles.
  - *Modo Riel Compacto (`sidebar_mini=True`):* Ancho forzado de 72px, textos ocultos mediante `.stSidebar .stButton button p { display: none !important; }`, iconos SVG centrados y rotación a 180° del icono de colapso para indicar expansión.

#### 6.7 Modal de Configuración Compacto (Sin Scroll)
- **Cambio:** Se eliminaron 6 separadores pesados `st.divider()`, se organizaron los controles en 2 columnas (Tema Visual junto a Filtros EPP; Motor IA junto a Sesión Activa) y se redujo el padding y espaciado vertical (`div[data-testid="stDialog"] { gap: 0.45rem }`). Todo el panel se visualiza en una sola vista sin requerir scroll.
- **Eliminación de advertencias:** Se eliminó la llamada redundante a `st.rerun()` dentro de los callbacks `on_change`, suprimiendo la alerta de advertencia en cabecera.

#### 6.8 Tarjeta Pericial Dinámica con Tokens Semánticos
- **Cambio:** La tarjeta de diagnóstico en la sección de Reportes sustituyó los fondos oscuros fijos por tokens semánticos del sistema (`var(--bg-card)`, `var(--border-subtle)`, `var(--text-primary)`, `var(--text-secondary)`).
- **Resultado:** Visualización limpia, nítida y con alto contraste tanto en Modo Claro como en Modo Oscuro.

---

### v4.3 — Arquitectura Modular, Pipeline Zero-Copy BGR y Clases Utilitarias (2026-10-22)

#### 6.9 Desacoplamiento de Vistas en `modules/views/`
- **Cambio:** `app.py` se redujo de 1,154 a 179 líneas (-84%), operando como orquestador declarativo de enrutamiento y sesión.
- **Estructura Modular:** Las interfaces se dividieron en responsabilidades aisladas:
  - `components.py`: Componentes de interfaz compartidos (presets de red, selector de dispositivos, cards HUD).
  - `config_dialog.py`: Modal emergente `@st.dialog` de configuración global.
  - `demo_view.py`: Sandbox de demostración en memoria para video, imágenes estáticas y sintéticos.
  - `live_view.py`: Panel de análisis continuo, telemetría y supervisión de planta.
  - `stats_view.py`: Métricas ejecutivas, gráficos de control SPC y calculadora de ROI.
  - `reports_view.py`: Dictamen pericial, bitácora forense y exportación oficial en HTML/PDF y CSV.

#### 6.10 Pipeline Gráfico Zero-Copy BGR Nativo
- **Cambio:** Inferencia con YOLOv8 y renderizado de anotaciones operan directamente en formato BGR nativo (`return_rgb=False`), entregando los fotogramas directamente a `LatestFrameNativeViewer.publish(frame_bgr)` sin conversiones intermedias `cv2.cvtColor`.
- **Razón:** Erradicar la sobrecarga de CPU y memoria de la doble conversión bidireccional `BGR -> RGB -> BGR` por cuadro a 20-30 FPS.

#### 6.11 Núcleo Común de Inferencia (`modules/auditor_core.py`)
- **Cambio:** Creación de `BaseAuditorService` y `annotate_auditor_frame`, unificando el ciclo de vida del hilo demonio, pacing de FPS, rotulado de operarios y preview Win32.
- **Desacoplamiento:** Se eliminaron ~400 líneas duplicadas entre `LiveAuditorService` (persistencia SQLite WAL y almacenamiento en disco) y `DemoVideoService` (almacenamiento en memoria RAM con `deque(maxlen=6)`), conectadas mediante el hook `_on_worker_event_confirmed`.

#### 6.12 Persistencia SQLite WAL con Actualización Atómica y Poda de Wrappers
- **Cambio:** `log_camera_event` consolida la inserción y el incremento de contadores de sesión en una sola transacción atómica, eliminando dos `COUNT(*)` redundantes por cada infracción.
- **Agregación Condicional:** `get_compliance_stats` unifica las métricas en un único escaneo de índice con `COALESCE(SUM(CASE ...), 0)`.
- **Poda de Wrappers:** Eliminación de 8 pasarelas vacías en `modules/metrics.py`, conectando la UI directamente con `modules.database`.

#### 6.13 Eliminación de Estilos Inline en Favor de Clases Utilitarias CSS
- **Cambio:** Sustitución de etiquetas HTML `<div style="...">` hardcodeadas en vistas por clases utilitarias semánticas integradas en `styles/styles.py`.

---

### v4.4 — Refinamiento Integral de Frontend, Controles de Potencia y Estilización de Widgets (2026-10-23)

#### 6.14 Modo Claro Predeterminado y Sincronización Global
- **Cambio:** `.streamlit/config.toml` y `app.py` establecen el Modo Claro como base predeterminada del sistema (`base = "light"`, `primaryColor = "#0284C7"`, `is_dark = False`), manteniendo soporte reactivo instantáneo a Modo Oscuro (`#00A8E8`).

#### 6.15 Controles de Potencia Reactivos (`st.toggle`)
- **Cambio:** Sustitución de los botones de iniciar/detener cámara en `modules/views/live_view.py` y `modules/views/demo_view.py` por interruptores deslizantes `st.toggle` ("Cámara Activa" y "Demostración Activa").
- **Beneficio:** Reducción de ruido visual, estado binario claro y alineación con los principios de diseño sobrio e industrial.

#### 6.16 Inversión Reactiva de Canvas para Dataframes en Modo Oscuro (`st.dataframe`)
- **Cambio:** En `styles/styles.py`, aplicación de filtro reactivo `filter: invert(0.92) hue-rotate(180deg) brightness(1.02) contrast(1.05) !important;` exclusivamente sobre el elemento `canvas` del componente `stDataFrame` cuando `is_dark=True`.
- **Beneficio:** Convierte el fondo blanco nativo del canvas de Glide Data Grid en fondo oscuro integrado con el tema sin alterar los colores de las fuentes ni generar fondos blancos deslumbrantes.

#### 6.17 Tarjetas de Métricas Nativas (`st.metric`) con Alto Contraste
- **Cambio:** Ampliación de selectores CSS para `stMetric` (`[data-testid="stMetricLabel"]`, `div[data-testid="stMetricValue"]`) para garantizar legibilidad óptima de números KPI en `JetBrains Mono` tabular y etiquetas en mayúsculas semánticas en ambos modos cromáticos.

#### 6.18 Widgets BaseWeb con Paleta Corporativa (`st.toggle` y `st.checkbox`)
- **Cambio:** Reemplazo de los tonos rojos nativos de Streamlit en interruptores y casillas de verificación. Los switches inactivos muestran fondo `--border-strong`, switches activos y checkboxes marcados muestran `--brand-primary` (`#0284C7` / `#00A8E8`) con checkmark vectorial blanco nítido.

#### 6.19 Deslizadores Globales Unificados en Azul (`hue-rotate(200deg)`)
- **Cambio:** Unificación cromática de los controles deslizantes (`st.select_slider` en Configuración y `st.slider` en Estadísticas) mediante rotación limpia de matiz `filter: hue-rotate(200deg)` sobre el contenedor `[data-baseweb="slider"]`, sin selectores conflictivos sobre los hijos.
- **Resultado:** Pista activa, botón circular y texto flotante ("Media", "Alta") convergen en azul corporativo homogéneo, eliminando distorsiones cromáticas y desajustes de color entre pista y selector.

#### 6.20 Amplitud Ejecutiva y Depuración de API en Modal de Configuración
- **Cambio:** En `modules/views/config_dialog.py`, se expandió el modal a `@st.dialog("Configuracion del Sistema", width="medium")` y se incrementó el margen vertical del encabezado del deslizador (22px).
- **Depuración:** Se eliminó el parámetro redundante `value=...` en widgets vinculados a `st.session_state` con `key`, erradicando las advertencias de Session State API al abrir el modal.

---

## 7. Clases Utilitarias CSS y Componentes UI (`styles/styles.py`)

Para garantizar coherencia visual, facilidad de mantenimiento y apego estricto a tokens de diseño, se consolidaron clases utilitarias semánticas inyectadas en `get_theme_css()`:

| Clase CSS | Propósito / Elemento | Propiedades Principales |
| :--- | :--- | :--- |
| `.section-header` | Encabezados de controles y selectores | `font-size: 0.75rem`, `font-weight: 700`, `text-transform: uppercase`, `letter-spacing: 0.04em`, `color: var(--text-secondary)` |
| `.preset-hint` | Subtítulo descriptivo de plantillas de conexión | `font-size: 0.72rem`, `color: var(--text-secondary)`, márgenes verticales controlados |
| `.feed-header` | Rótulo superior para feeds de incidentes en tiempo real | `font-size: 0.75rem`, `font-weight: 700`, `text-transform: uppercase`, `color: var(--brand-primary)` |
| `.status-indicator-stopped` | Rótulo de cámara detenida | `text-align: center`, `font-size: 0.78rem`, `font-weight: 700`, `color: var(--text-secondary)` |
| `.status-indicator-running` | Rótulo de cámara en vivo | `text-align: center`, `font-size: 0.78rem`, `font-weight: 700`, `color: #10B981` |
| `.hud-card` | Contenedor informativo de ventana de escritorio | `background: var(--bg-card)`, `border: 1px solid var(--border-subtle)`, `border-left: 5px solid var(--brand-primary)`, `border-radius: 8px`, `padding: 28px 20px` |
| `.hud-card-title` | Título de aviso de ventana nativa | `font-size: 1.15rem`, `font-weight: 800`, `color: var(--brand-primary)`, `margin-bottom: 8px` |
| `.hud-card-desc` | Descripción de ventana nativa | `font-size: 0.88rem`, `color: var(--text-secondary)`, `max-width: 520px`, `line-height: 1.45` |
| `.layout-spacer` | Separador de flujo visual | `margin-top: 8px`, `margin-bottom: 8px` |
| `.badge-indicator` | Indicador de estado en bitácoras | `display: inline-flex`, `align-items: center`, `gap: 4px`, `font-size: 0.68rem`, `font-weight: 800`, `padding: 2px 8px`, `border-radius: 4px` |
| `.kpi-subtext` | Metadatos y subtítulos técnicos | `font-size: 0.80rem`, `color: var(--text-secondary)`, `line-height: 1.3` |

---

## 8. Estándar de Visión Artificial BGR y Núcleo de Inferencia (`modules/auditor_core.py`)

### 8.1 Representación Cromática en Inferencia
El pipeline de visión opera 100% en el espacio de color **BGR** nativo de OpenCV, evitando conversiones innecesarias:

- **Verde Conforme (`safe`):** `(0, 220, 110)` en BGR.
- **Rojo Peligro / Infracción (`danger`):** `(0, 60, 240)` en BGR.
- **Ámbar Advertencia (`warning`):** `(0, 200, 255)` en BGR.
- **Fondo HUD Superior:** `(42, 23, 15)` en BGR (Azul Marino Abisal).

### 8.2 Anotación Gráfica Unificada (`annotate_auditor_frame`)
- **Etiquetas de Operario:** Recuadro delimitador con etiqueta superior o inferior auto-ajustable (`#Operario-XX | OK` o `#Operario-XX | INFRACCIÓN`) con tipografía `FONT_HERSHEY_SIMPLEX` a escala `0.45`.
- **Banner HUD Semafórico:** Banda superior de 36px de alto con estado general de la planta (`REC [MOT TRACKING] | {TITULO}`), grosor de trazo `2` y renderizado antialiasing (`LINE_AA`).

### 8.3 Núcleo `BaseAuditorService`
- Hilo demonio con control de cadencia FPS monotónico (`max(0.015, 0.045 - elapsed)`).
- Publicación no bloqueante en $O(1)$ hacia `LatestFrameNativeViewer` en hilo Win32 dedicado (`NativeViewerOwner`) a ~50 FPS.
- Desacoplamiento de almacenamiento a través del hook abstracto `_on_worker_event_confirmed(event_payload)`.

---

## 9. Reglas Anti-Slop, Prohibición de Emojis y Código Limpio

En cumplimiento de las directrices de ingeniería y anti-slop del proyecto:

1. **Prohibición Total de Emojis:** Queda terminantemente prohibido el uso de emojis en interfaces, botones, etiquetas, código fuente, logs y documentación técnica. Únicamente se permite el uso de texto en español o glifos Unicode industriales sobrios (●, ■, ◈, ◉, ▲, ≡, ⚙).
2. **Higiene de Comentarios (`antislop-code`):**
   - Prohibidos los banners decorativos basados en caracteres repetidos (`# ===`, `# ---`, `// ===`).
   - Prohibidos los comentarios que se limitan a narrar la sintaxis obvia (`# Iniciar variable`, `# Selector de sesión`).
   - Preservar rigurosamente los comentarios que justifiquen restricciones de concurrencia (`CAMERA_MODE_LOCK`, modo WAL de SQLite, buffers $O(1)$) o requisitos de seguridad laboral.
3. **Arquitectura Sin Capas Fantasma:** Prohibidos los wrappers o interfaces artificiales de una sola línea que no aporten validación, transformación o valor técnico real.
4. **Respeto a la Suite de Pruebas:** Cualquier cambio de diseño o refactorización debe garantizar que la totalidad de pruebas automatizadas (39 tests unitarios) apruebe al 100% sin regresiones.
