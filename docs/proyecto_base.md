# 🛡️ SafeGuard AI: Detector de EPP en Tiempo Real
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

## 3. Estructura de la Aplicación Web (3 Pestañas Esenciales)

La interfaz se divide en 3 vistas clave enfocadas en captar la atención del público y del jurado:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        🛡️ SafeGuard AI - Dashboard                      │
├────────────────────────────────────────────────────────────────────────┤
│  [ Pestaña 1: Monitoreo en Vivo ] [ Pestaña 2: Análisis ] [ Pestaña 3: Métricas & ROI ] │
└────────────────────────────────────────────────────────────────────────┘
```

---

### 🔹 Pestaña 1: Monitoreo en Vivo (Live Webcam)
* **Objetivo:** Demostración en vivo en el stand de la feria.
* **Elementos Esenciales:**
  1. **Interruptor de Cámara:** Iniciar / Detener transmisión de la webcam.
  2. **Checklist de EPP Activo:** Filtros de seguridad a auditar (`[x] Casco de Seguridad`, `[x] Chaleco Reflectante`, `[x] Gafas`).
  3. **Visor de Video en Tiempo Real:** 
     * Recuadro 🟢 **Verde** cuando se detecta el EPP reglamentario.
     * Recuadro 🔴 **Rojo** cuando se detecta la persona sin el equipo requerido.
  4. **Semáforo de Estado en Vivo:** Alerta visual destacada en pantalla: `ESTADO: SEGURO (100% EPP)` o `ALERTA: INFRACCIÓN DETECTADA`.

---

### 🔹 Pestaña 2: Inspección de Archivos (Fotos y Videos)
* **Objetivo:** Mostrar cómo funcionaría el sistema en fotos o grabaciones de obras industriales reales.
* **Elementos Esenciales:**
  1. **Selector de Imágenes de Muestra:** Botones rápidos (`Ejemplo 1: Obrero con EPP completo`, `Ejemplo 2: Obrero sin Casco`) para demostraciones rápidas en 1 clic.
  2. **Carga Manual:** Opción para subir imágenes (`.jpg`, `.png`) desde la computadora.
  3. **Visualización Lado a Lado:** Imagen original vs. Imagen analizada con cajas de detección y etiquetas de confianza (%).
  4. **Resumen de Hallazgos:** Tabla con el listado de personas y elementos encontrados.

---

### 🔹 Pestaña 3: Métricas de Seguridad & Calculadora de ROI (Pitch Empresarial)
* **Objetivo:** Demostrar a los evaluadores que no es solo un detector, sino una solución rentable para empresas.
* **Elementos Esenciales:**
  1. **KPI Cards:**
     * `% Cumplimiento de Normativa EPP`
     * `Infracciones Prevenidas`
     * `Tasa de Reducción de Riesgo`
  2. **Gráfico Estadístico:** Distribución de faltas más comunes (ej. Falta de Casco vs. Falta de Chaleco).
  3. **Calculadora Interactiva de Ahorro:**
     * Control deslizable para ingresar número de trabajadores de la empresa.
     * Cálculo automático de ahorro anual estimado en multas laborales y reducción de costos de seguro.

---

## 4. Guía del Pitch para la Feria (2 Minutos)

1. **Problema (30 seg):** Explicar el impacto de los accidentes por falta de EPP y la limitación de la supervisión humana tradicional.
2. **Demo en Vivo (45 seg):** Activar la cámara en vivo en la Pestaña 1, mostrar la detección instantánea al ponerse/quitarse el EPP.
3. **Casos Reales y Escalabilidad (20 seg):** Pasar a la Pestaña 2 y mostrar el análisis sobre fotos de plantas industriales.
4. **Propuesta Económica (25 seg):** Cerrar en la Pestaña 3 con la calculadora de ahorro y el modelo de software integrable con cámaras CCTV ya instaladas.

---

## 5. Instrucciones de Instalación y Ejecución

1. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Iniciar la aplicación:**
   ```bash
   streamlit run app.py
   ```
3. Se abrirá automáticamente en tu navegador web en `http://localhost:8501`.
