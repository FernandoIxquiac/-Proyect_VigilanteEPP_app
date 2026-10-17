# Directrices para Agentes en el Proyecto EPP

Este archivo define las convenciones de código, arquitectura y buenas prácticas que todos los agentes (principales o subagentes) deben seguir al trabajar en este repositorio.

---

## 1. Stack Tecnológico y Entorno
- **Lenguaje Principal:** Python 3.x
- **Interfaz y UI:** Streamlit (`app.py`, `.streamlit/`)
- **Estructura Modular:** El código reutilizable y la lógica de negocio deben ubicarse en `modules/` o `scripts/`.
- **Modelos y Datos:** Archivos de modelos en `models/` y recursos/datos en `data/` o `assets/`.

---

## 2. Reglas de Desarrollo y Código
- **Prohibición Total de Emojis:** PROHIBIDO EL USO DE EMOJIS en la interfaz de usuario, etiquetas, botones, logs, código fuente y documentación técnica. Utilizar únicamente texto en español o glifos Unicode industriales sobrios (ej. ●, ■, ◈, ◉, ▲, ≡, ⚙).
- **Estilo de Código:** Seguir las convenciones de PEP 8, nombres descriptivos en variables y funciones.
- **Modularidad:** Evitar añadir lógica pesada directamente en la capa de presentación (`app.py`); delegar la lógica a `modules/`.
- **Manejo de Errores y Logs:** Capturar excepciones específicas en lugar de bloques genéricos `except Exception:`.
- **Integridad:** Respetar los comentarios y docstrings existentes a menos que se solicite explícitamente su refactorización.

---

## 3. Seguridad y Archivos Sensibles
- No colocar credenciales, claves API o rutas absolutas fijas en el código.
- Verificar el `.gitignore` antes de generar archivos temporales, datasets o pesos de modelos pesados.

---

## 4. Subagentes Disponibles
Los subagentes personalizados para este proyecto se configuran dentro de `.agents/agents/`.
- `planner-lead`: Planificación y diseño de arquitectura.
- `coder-flash`: Implementación quirúrgica de código.
- `qa-verifier`: Control de calidad y verificación de tests.
- `code-reviewer`: Auditoría de código, buenas prácticas y optimización.

---

## 5. Política de Modelos para Subagentes
Actualmente configurado para operar 100% con **Gemini 3.8 Flash High** (aprovechando cuota disponible y modo thinking):
- **Planificación (`planner-lead`) y Verificación (`qa-verifier`, `code-reviewer`):** Operar con **`gemini-3.8-flash`** con `thinkingLevel: high` para asegurar razonamiento profundo, prevención de errores y análisis de código.
- **Ejecución y Codificación (`coder-flash`):** Operar con **`gemini-3.8-flash`** con `thinkingLevel: high` para implementación ágil y precisa siguiendo estrictamente el plan.
*(Nota: Cuando se restablezca la cuota de Claude, los roles de planificación y verificación pueden retornar opcionalmente a `claude-sonnet`).*



