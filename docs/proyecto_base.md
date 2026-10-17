# SafeGuard AI: Detector de EPP en Tiempo Real
> **Documento Base del Proyecto - Edición Feria de Emprendimiento**

---

## 1. Resumen Ejecutivo y Propuesta de Valor

* **Problema:** En sectores como minería, manufactura y construcción, más del 40% de accidentes graves ocurren por falta de uso o uso indebido de EPP (casco, chaleco reflectante, gafas, guantes). La supervisión humana tradicional es intermitente, costosa y propensa al error.
* **Solución:** **SafeGuard AI**, una plataforma de visión por computadora que analiza transmisiones de video en tiempo real, detecta automáticamente la presencia o ausencia de EPP reglamentario y genera alertas visuales inmediatas para prevenir accidentes antes de que ocurran.
* **Diferencial para la Feria:** Demostración 100% interactiva en vivo con cámara web o fotos de prueba, métricas de cumplimiento instantáneas y calculadora de retorno de inversión (ahorro en multas y pólizas de seguro).

---

## 2. Stack Tecnológico Sugerido (Foco en Viabilidad y Cero Complejidad)

Para garantizar que el demo funcione sin fallos, sin requerir servidores externos ni configuraciones complejas:

| Componente | Tecnología | Justificación |
| :--- | :--- | :--- |
| **Lenguaje** | **Python 3.9+** | Estándar en Inteligencia Artificial, limpio y fácil de explicar. |
| **Frontend / Web App** | **Streamlit** | Permite construir una interfaz visual moderna, reactiva y profesional directamente desde Python en menos de 200 líneas de código. |
| **Detección de IA** | **Ultralytics YOLOv8 / YOLO11** | La arquitectura más rápida y precisa para detección de objetos en tiempo real, corre directamente en laptops sin tarjeta gráfica dedicada. |
| **Tratamiento de Imagen** | **OpenCV (`cv2`)** | Captura fluida de cámara web, anotaciones gráficas y visualización. |
| **Métricas y Datos** | **Pandas & Altair/Plotly** | Gráficos interactivos en tiempo real integrados de forma nativa en Streamlit. |

---

## 3. Estructura de la Aplicación Web (5 Secciones con Sidebar)

La interfaz se organiza en un menú lateral de navegación sobrio y moderno con acceso rápido a las secciones clave:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        SafeGuard AI - Dashboard                        │
├───────────────────┬────────────────────────────────────────────────────┤
│  Navegación       │  Vista Principal Activa                            │
│  ──────────       │  ──────────────────────                            │
│  ◈ Demostración   │  Sandbox: prueba sin almacenar en BD               │
│  ◉ Análisis Vivo  │  Webcam/RTSP en vivo + Tracking MOT + Semáforo HUD │
│  ▲ Estadísticas   │  Control Estadístico SPC + KPIs + Calculadora ROI  │
│  ≡ Reportes       │  Bitácora pericial (ISO/OSHA) + HTML/CSV           │
│  ──────────────── │                                                    │
│  ⚙ Configuración  │  Modal (@st.dialog): Sensibilidad, Tema y Filtros  │
└───────────────────┴────────────────────────────────────────────────────┘
```

---

### Sección 1: Demostración (Sandbox de Pruebas)
* **Objetivo:** Demostración interactiva inmediata sin alterar la base de datos operativa.
* **Elementos Esenciales:**
  1. **Banner Informativo:** Indicador visual de modo demostración activo (sin persistencia).
  2. **Selector de Escenas Sintéticas:** Casos simulados de prueba (`Obrero con EPP Completo`, `Infracción Falta de Casco`).
  3. **Carga Manual:** Subida de fotografías locales (`.jpg`, `.png`).
  4. **Comparador Visual Lado a Lado:** Imagen original vs. Análisis con detección YOLOv8.
  5. **Desglose de Hallazgos por Trabajador:** Tabla con verificación individual de casco, chaleco y veredicto.

---

### Sección 2: Análisis en Vivo (Monitoreo en Tiempo Real)
* **Objetivo:** Monitoreo activo continuo por webcam o flujo IP con registro automático de auditorías.
* **Elementos Esenciales:**
  1. **Selectores de Dispositivo y Modo:** Compatibilidad con webcam integrada, externa USB, flujo RTSP y modo Snapshot.
  2. **Transmisión Fluida Desacoplada:** Captura multihilo en segundo plano que previene interrupciones de hardware.
  3. **Tracking Multi-Operario (ByteTrack):** Persistencia de IDs entre cuadros y prevención de registros duplicados.
  4. **Semáforo HUD y Feed de Últimas Auditorías:** Estado normativo (`SEGURO`, `ADVERTENCIA`, `CRÍTICO`) y tarjetas en vivo.

---

### Sección 3: Estadísticas (Control de Procesos & ROI)
* **Objetivo:** Análisis estadístico para toma de decisiones gerenciales y pitch financiero de rentabilidad.
* **Elementos Esenciales:**
  1. **Filtro por Sesión / Turno:** Análisis de sesiones individuales o consolidado histórico global.
  2. **KPIs Ejecutivos:** Total de auditorías, tasa de cumplimiento, infracciones y ROI estimado.
  3. **Gráficos SPC y Severidad:** Control Estadístico de Procesos (Shewhart Run Chart) y distribución de riesgo.
  4. **Calculadora Interactiva de ROI:** Deslizadores de trabajadores y multas promedio con proyección de ahorro anual.

---

### Sección 4: Reportes (Auditoría Forense y Exportación)
* **Objetivo:** Cumplimiento normativo legal (ISO 45001 / OSHA 1910) y peritaje exportable.
* **Elementos Esenciales:**
  1. **Diagnóstico Pericial Automatizado:** Tarjeta de apego normativo e infracción predominante.
  2. **Filtros por Riesgo y Operario:** Filtrado específico de eventos críticos y trazabilidad por trabajador.
  3. **Galería de Evidencias Fotográficas:** Muestra visual de capturas asociadas a infracciones detectadas.
  4. **Exportación Oficial:** Generación y descarga de informes formales en HTML (listos para PDF con Ctrl+P) y bitácora en CSV.

---

### Modal de Configuración (@st.dialog)
* **Objetivo:** Panel de control centralizado accesible desde el sidebar sin recargar la navegación.
* **Elementos Esenciales:** Conmutador de Tema Oscuro/Claro, filtros de EPP (Casco, Chaleco), umbral de sensibilidad (%) y gestión de turno activo.

---

## 4. Guía del Pitch para la Feria (2 Minutos)

1. **Problema (30 seg):** Explicar el impacto de los accidentes por falta de EPP y la limitación de la supervisión humana tradicional.
2. **Demo en Vivo (45 seg):** Activar la cámara en la sección **◉ Análisis en Vivo**, mostrar la detección instantánea al ponerse/quitarse el EPP.
3. **Casos y Trazabilidad (20 seg):** Mostrar **◈ Demostración** con fotos reales y la bitácora pericial en **≡ Reportes**.
4. **Propuesta Económica (25 seg):** Cerrar en **▲ Estadísticas** con la calculadora de ROI y el modelo integrable con CCTV.

---

## 5. Instrucciones de Instalación y Ejecución

1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Ejecutar la aplicación:**
   ```bash
   streamlit run app.py
   ```
