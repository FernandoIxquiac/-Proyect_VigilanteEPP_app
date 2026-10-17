# PLAN DE CORRECCION DE FALLOS VISUALES Y DE ESTADO — VIGILANTE EPP

## Objetivo
Resolver de forma definitiva los 2 fallos reportados con evidencia visual:
1. Visibilidad y contraste de fuentes en todas las pantallas (widgets de radio horizontal, captions, alertas st.info, selectbox, labels y botones).
2. Persistencia y valores predeterminados del menu de configuracion (Modo Oscuro en ON, Casco en ON, Chaleco en ON, Sensibilidad en Media por defecto; guardado permanente en session_state.config que no se borra al cerrar o reabrir el menu).

---

## Tarea 1: Correccion de Visibilidad de Fuentes y Contraste CSS (styles/styles.py)
1. **Radio buttons en horizontal y vertical (Modo de Video, etc.):**
   - Asegurar que `div[data-testid="stRadio"] label p`, `div[data-testid="stRadio"] label div`, `div[data-testid="stRadio"] label span`, `div[role="radiogroup"] label *` tengan `color: var(--text-primary) !important;` y `font-weight: 500 !important;`.
   - En el Sidebar: `.stSidebar div[data-testid="stRadio"] label p` y `*` con `color: var(--text-primary) !important; font-weight: 600 !important;`.
2. **Textos secundarios y st.caption:**
   - Forzar `div[data-testid="stCaptionContainer"] p`, `div[data-testid="stCaptionContainer"] *`, `.stCaption`, `.stCaption p`, `small` a `color: var(--text-secondary) !important; font-size: 0.82rem !important;`.
3. **Alertas y Cajas de Informacion (st.info, st.warning, st.error):**
   - En `div[data-testid="stAlert"]`: fondo `var(--bg-elevated) !important;`, borde `var(--border-strong) !important;` y borde izquierdo `4px solid var(--brand-primary) !important;`.
   - `div[data-testid="stAlert"] *`, `div[data-testid="stAlert"] p`: `color: var(--text-primary) !important;`.
   - Icono SVG: `fill: var(--brand-primary) !important;`.
4. **Selectbox e Inputs:**
   - `div[data-baseweb="select"] *`, `div[data-baseweb="select"] div`, `div[data-baseweb="select"] span`: `color: var(--text-primary) !important;`.
   - `label[data-testid="stWidgetLabel"]`, `label[data-testid="stWidgetLabel"] *`, `label[data-testid="stWidgetLabel"] p`: `color: var(--text-primary) !important; font-weight: 600 !important;`.
5. **Checkboxes y Toggles:**
   - `div[data-testid="stCheckbox"] label *`, `div[data-testid="stCheckbox"] label p`, `div[data-testid="stToggle"] label *`, `div[data-testid="stToggle"] label p`: `color: var(--text-primary) !important; font-weight: 500 !important;`.
6. **Sliders:**
   - `div[data-testid="stSlider"] *`, `div[data-testid="stSlider"] p`, `div[data-testid="stSlider"] span`, `div[data-baseweb="slider"] *`: `color: var(--text-primary) !important;`.
7. **Botones en Sidebar y Dialogo:**
   - `.stSidebar .stButton > button`: fondo `var(--bg-card) !important;`, color `var(--text-primary) !important;`, borde `1px solid var(--border-strong) !important;`.
   - `.stSidebar .stButton > button *`: `color: var(--text-primary) !important;`.
   - Hover: fondo `var(--brand-primary-soft) !important;`, color `var(--brand-primary) !important;`.
8. **Iconos de Tooltips (?):**
   - `div[data-testid="stTooltipIcon"] svg`, `div[data-testid="stTooltipIcon"] *`: `fill: var(--text-secondary) !important; color: var(--text-secondary) !important;`.

---

## Tarea 2: Persistencia y Valores Predeterminados Blindados (app.py)
1. **Estructura maestra persistente:**
   - Crear `st.session_state.config`:
     ```python
     if "config" not in st.session_state:
         st.session_state.config = {
             "is_dark": True,
             "check_helmet": True,
             "check_vest": True,
             "sensitivity_mode": "Media",
             "conf_threshold_pct": 45
         }
     ```
   - Sincronizar hacia claves compatibles en `st.session_state`: `is_dark`, `check_helmet`, `check_vest`, `conf_threshold_pct`.
2. **Modal de Configuracion config_dialog():**
   - Leer siempre de `st.session_state.config`.
   - Widgets con claves dedicadas `dlg_is_dark`, `dlg_helmet`, `dlg_vest`, `dlg_sensitivity` y `value=cfg[...]`.
   - Callbacks reactivos que actualizan inmediatamente `st.session_state.config[...]` y ejecutan `st.rerun()`.
   - Así, al abrir por primera vez:
     - Modo Oscuro: ON (True)
     - Casco: Marcado (True)
     - Chaleco: Marcado (True)
     - Sensibilidad: Media (45%)
   - Y al cambiar cualquiera de ellos, se guarda permanentemente y al volver a abrir el diálogo SIEMPRE se conservan los valores elegidos por el usuario.

---

## Verificacion
- Compilar con `python -m py_compile app.py styles/styles.py`.
- Verificar que no queden errores de sintaxis y que las variables sean leidas correctamente.
