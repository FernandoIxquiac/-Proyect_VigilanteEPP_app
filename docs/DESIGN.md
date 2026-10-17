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
6. [Solución Definitiva a Componentes Nativos de Streamlit](#6-solución-definitiva-a-componentes-nativos-de-streamlit)
7. [Especificación de Componentes UI (`styles/styles.py`)](#7-especificación-de-componentes-ui-stylesstylespy)
8. [Estándar Visual en Video/IA (`modules/detector.py`)](#8-estándar-visual-en-videoia-modulesdetectorpy)
9. [Estándar para Gráficos (`modules/charts.py`) e Informes (`report_generator.py`)](#9-estándar-para-gráficos-moduleschartspy-e-informes-report_generatorpy)

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