import streamlit as st

def get_theme_css(is_dark: bool = True) -> str:
    """Genera el CSS global de alto contraste según el modo (Claro / Oscuro)."""
    if is_dark:
        bg_main = "#0b1326"
        bg_card = "#171f33"
        bg_sidebar = "#131b2e"
        text_primary = "#f8fafc"
        text_muted = "#cbd5e1"
        border_color = "#424754"
        accent_blue = "#60a5fa"
        tab_bg = "#131b2e"
        tab_active_bg = "#222a3d"
    else:
        bg_main = "#f8fafc"
        bg_card = "#ffffff"
        bg_sidebar = "#f1f5f9"
        text_primary = "#0f172a"
        text_muted = "#334155"
        border_color = "#cbd5e1"
        accent_blue = "#1d4ed8"
        tab_bg = "#e2e8f0"
        tab_active_bg = "#ffffff"

    return f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

    /* Reduce whitespace and constrain to compact centered industrial cockpit */
    .block-container {{
        max-width: 1180px !important;
        margin-left: auto !important;
        margin-right: auto !important;
        padding-top: 1.0rem !important;
        padding-bottom: 1rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
    }}

    /* Global App Background and Text */
    .stApp {{
        background-color: {bg_main} !important;
        color: {text_primary} !important;
        font-family: 'Inter', sans-serif !important;
    }}

    /* Force text color on all generic markdown, headers, and labels */
    .stApp p, .stApp span, .stApp label, .stApp div, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {{
        color: {text_primary} !important;
    }}

    /* Sidebar Styling & Contrast */
    section[data-testid="stSidebar"] {{
        background-color: {bg_sidebar} !important;
        border-right: 1px solid {border_color} !important;
    }}
    section[data-testid="stSidebar"] * {{
        color: {text_primary} !important;
    }}
    section[data-testid="stSidebar"] .stMarkdown p {{
        color: {text_muted} !important;
    }}

    /* Widget Labels (Checkboxes, Radios, Sliders, Toggles) */
    .stCheckbox label span, .stRadio label span, .stSlider label span, .stToggle label span, div[data-testid="stToggle"] label p {{
        color: {text_primary} !important;
        font-weight: 600 !important;
    }}

    /* Live Camera & Image Frame Viewport Fitting & Perfect Centering */
    div[data-testid="stImage"] {{
        display: flex !important;
        justify-content: center !important;
        align-items: center !important;
        width: 100% !important;
        text-align: center !important;
        margin: 0 auto !important;
    }}
    div[data-testid="stImage"] img {{
        max-height: 430px !important;
        width: 100% !important;
        max-width: 100% !important;
        object-fit: contain !important;
        border-radius: 8px !important;
        border: 1px solid #334155 !important;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.25) !important;
        margin: 0 auto !important;
        display: block !important;
    }}



    /* Tabs Styling */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: {tab_bg};
        padding: 5px;
        border-radius: 10px;
        border: 1px solid {border_color};
        margin-bottom: 12px;
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px;
        padding: 6px 14px;
        color: {text_muted} !important;
        font-weight: 600 !important;
        border: none !important;
        background-color: transparent !important;
    }}
    .stTabs [aria-selected="true"] {{
        background-color: {tab_active_bg} !important;
        color: {accent_blue} !important;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }}
    .stTabs [aria-selected="true"] span, .stTabs [aria-selected="true"] p {{
        color: {accent_blue} !important;
        font-weight: 700 !important;
    }}

    /* Native Streamlit Header transparent & compact */
    header[data-testid="stHeader"], [data-testid="stHeader"] {{
        background-color: transparent !important;
        background: transparent !important;
        height: 2rem !important;
    }}

    /* Metric Cards Native Override - Compact Footer Style */
    div[data-testid="stMetric"] {{
        background-color: {bg_card} !important;
        border: 1px solid {border_color} !important;
        padding: 6px 12px !important;
        border-radius: 8px !important;
        min-height: 58px !important;
        display: flex !important;
        flex-direction: column !important;
        justify-content: center !important;
    }}
    div[data-testid="stMetricLabel"] p {{
        color: {text_muted} !important;
        font-size: 0.70rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.03em !important;
        margin-bottom: 0px !important;
    }}
    div[data-testid="stMetricValue"] div {{
        color: {text_primary} !important;
        font-size: 1.25rem !important;
        font-weight: 800 !important;
        font-variant-numeric: tabular-nums !important;
        line-height: 1.2 !important;
    }}


    /* Charts (st.bar_chart, st.line_chart / Vega-Lite) Theme Adaptation */
    div[data-testid="stArrowVegaLiteChart"] {{
        background-color: {bg_card} !important;
        border: 1px solid {border_color} !important;
        border-radius: 10px !important;
        padding: 12px !important;
    }}
    div[data-testid="stArrowVegaLiteChart"] svg {{
        background-color: transparent !important;
        background: transparent !important;
    }}
    div[data-testid="stArrowVegaLiteChart"] .vega-embed {{
        background-color: transparent !important;
        background: transparent !important;
    }}
    div[data-testid="stArrowVegaLiteChart"] text {{
        fill: {text_muted} !important;
    }}
    div[data-testid="stArrowVegaLiteChart"] line {{
        stroke: {border_color} !important;
    }}

    /* Form Controls & Dropdowns (Selectbox, Inputs, Modals) */
    div[data-baseweb="select"],
    div[data-baseweb="select"] > div,
    div[data-baseweb="select"] div,
    div[data-baseweb="select"] span,
    div[data-testid="stSelectbox"] > div,
    div[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input {{
        background-color: {bg_card} !important;
        color: {text_primary} !important;
        border-color: {border_color} !important;
    }}
    div[data-baseweb="select"] svg {{
        fill: {text_primary} !important;
        color: {text_primary} !important;
    }}
    div[data-baseweb="popover"],
    div[data-baseweb="popover"] ul,
    div[data-baseweb="popover"] li,
    div[data-baseweb="menu"],
    ul[data-testid="stSelectboxVirtualDropdown"],
    li[data-testid="stSelectboxVirtualDropdown-item"] {{
        background-color: {bg_card} !important;
        color: {text_primary} !important;
        border-color: {border_color} !important;
    }}
    ul[data-testid="stSelectboxVirtualDropdown"] li:hover,
    li[data-testid="stSelectboxVirtualDropdown-item"]:hover {{
        background-color: {tab_active_bg} !important;
        color: {accent_blue} !important;
    }}

    /* Custom Buttons Universal */
    button[kind="secondary"],
    button[kind="primary"],
    .stButton > button,
    div[data-testid="stButton"] button,
    button[data-testid="baseButton-secondary"] {{
        border-radius: 8px !important;
        font-weight: 600 !important;
        border: 1px solid {border_color} !important;
        color: {text_primary} !important;
        background-color: {bg_card} !important;
    }}
    button[kind="secondary"]:hover,
    .stButton > button:hover,
    div[data-testid="stButton"] button:hover {{
        border-color: {accent_blue} !important;
        color: {accent_blue} !important;
        background-color: {tab_active_bg} !important;
    }}

    /* File Uploader Dropzone Styling */
    div[data-testid="stFileUploader"] {{
        background-color: transparent !important;
    }}
    div[data-testid="stFileUploader"] section[data-testid="stFileUploaderDropzone"],
    section[data-testid="stFileUploaderDropzone"],
    div[data-testid="stFileUploaderDropzone"] {{
        background-color: {bg_card} !important;
        border: 2px dashed {border_color} !important;
        border-radius: 10px !important;
        padding: 18px 24px !important;
        transition: all 0.2s ease-in-out !important;
    }}
    div[data-testid="stFileUploaderDropzone"]:hover,
    section[data-testid="stFileUploaderDropzone"]:hover {{
        border-color: {accent_blue} !important;
        background-color: {tab_active_bg} !important;
    }}
    div[data-testid="stFileUploaderDropzone"] *,
    section[data-testid="stFileUploaderDropzone"] * {{
        color: {text_primary} !important;
    }}
    div[data-testid="stFileUploaderDropzone"] span,
    div[data-testid="stFileUploaderDropzone"] div,
    section[data-testid="stFileUploaderDropzone"] span,
    section[data-testid="stFileUploaderDropzone"] div {{
        color: {text_primary} !important;
        font-weight: 500 !important;
    }}
    div[data-testid="stFileUploaderDropzone"] small,
    section[data-testid="stFileUploaderDropzone"] small {{
        color: {text_muted} !important;
        font-size: 0.78rem !important;
    }}
    div[data-testid="stFileUploaderDropzone"] svg,
    section[data-testid="stFileUploaderDropzone"] svg {{
        fill: {accent_blue} !important;
        color: {accent_blue} !important;
    }}
    div[data-testid="stFileUploaderDropzone"] button,
    section[data-testid="stFileUploaderDropzone"] button {{
        background-color: {tab_active_bg} !important;
        color: {text_primary} !important;
        border: 1px solid {border_color} !important;
        border-radius: 6px !important;
        font-weight: 600 !important;
        padding: 6px 16px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
    }}
    div[data-testid="stFileUploaderDropzone"] button:hover,
    section[data-testid="stFileUploaderDropzone"] button:hover {{
        border-color: {accent_blue} !important;
        color: {accent_blue} !important;
        background-color: {bg_main} !important;
    }}
    /* Uploaded File Item Preview */
    div[data-testid="stFileUploaderFileData"] {{
        background-color: {bg_card} !important;
        border: 1px solid {border_color} !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
        color: {text_primary} !important;
    }}
    div[data-testid="stFileUploaderFileData"] * {{
        color: {text_primary} !important;
    }}
    div[data-testid="stFileUploaderDeleteBtn"] button {{
        color: {text_muted} !important;
    }}
    div[data-testid="stFileUploaderDeleteBtn"] button:hover {{
        color: #ef4444 !important;
    }}

    /* DataFrame and Table Dark Mode Override */
    div[data-testid="stDataFrame"], div[data-testid="stTable"] {{
        background-color: {bg_card} !important;
        border: 1px solid {border_color} !important;
        border-radius: 10px !important;
        padding: 6px !important;
    }}

    /* Expander / Accordion Theme Adaptation */
    div[data-testid="stExpander"],
    details[data-testid="stExpander"],
    details {{
        background-color: {bg_card} !important;
        border: 1px solid {border_color} !important;
        border-radius: 8px !important;
        margin-top: 6px !important;
        margin-bottom: 6px !important;
    }}
    details[data-testid="stExpander"] summary,
    div[data-testid="stExpander"] summary,
    summary[data-testid="stExpanderToggle"],
    details summary {{
        background-color: {bg_card} !important;
        color: {text_primary} !important;
        border-radius: 8px !important;
        padding: 8px 14px !important;
        font-weight: 600 !important;
        border: none !important;
    }}
    details[data-testid="stExpander"] summary:hover,
    div[data-testid="stExpander"] summary:hover,
    summary[data-testid="stExpanderToggle"]:hover,
    details summary:hover {{
        background-color: {tab_active_bg} !important;
        color: {accent_blue} !important;
    }}
    details summary p,
    details summary span,
    details summary div {{
        color: {text_primary} !important;
        font-weight: 600 !important;
    }}
    details summary svg {{
        fill: {text_primary} !important;
        color: {text_primary} !important;
    }}
    div[data-testid="stExpanderDetails"] {{
        background-color: {bg_card} !important;
        color: {text_primary} !important;
        border-top: 1px solid {border_color} !important;
        padding: 12px !important;
        border-bottom-left-radius: 8px !important;
        border-bottom-right-radius: 8px !important;
    }}
    div[data-testid="stExpanderDetails"] * {{
        color: {text_primary} !important;
    }}
</style>
"""

def apply_styles(theme_mode = "Modo Oscuro"):
    """Inyecta los estilos CSS globales según el modo elegido."""
    if isinstance(theme_mode, bool):
        is_dark = theme_mode
    else:
        is_dark = ("Oscuro" in str(theme_mode) or "Dark" in str(theme_mode))
    st.markdown(get_theme_css(is_dark), unsafe_allow_html=True)

def render_top_header(is_dark: bool = True) -> str:
    """Genera la barra superior HUD compacta para ganar espacio vertical."""
    bg_color = "#171f33" if is_dark else "#ffffff"
    border_color = "#424754" if is_dark else "#cbd5e1"
    sub_color = "#cbd5e1" if is_dark else "#475569"
    title_color = "#60a5fa" if is_dark else "#1d4ed8"

    return f'<div style="display:flex; justify-content:space-between; align-items:center; background-color:{bg_color}; border:1px solid {border_color}; border-radius:8px; padding:8px 16px; margin-bottom:8px;"><div style="display:flex; align-items:center; gap:8px;"><div style="font-size:13px; font-weight:900; font-family:monospace; color:{title_color}; background:rgba(96,165,250,0.12); border:1px solid rgba(96,165,250,0.3); padding:2px 6px; border-radius:4px;">EPP</div><div><div style="font-size:1.05rem; font-weight:800; color:{title_color}; letter-spacing:0.02em;">VIGILANTE EPP <span style="font-size:0.8rem; font-weight:600; color:{sub_color};">| Sistema 4.0</span></div><div style="font-size:0.7rem; color:{sub_color};">Deteccion Inteligente de Equipos de Proteccion Personal</div></div></div><div style="display:flex; align-items:center; gap:8px;"><span style="display:inline-flex; align-items:center; gap:4px; background:rgba(78, 222, 163, 0.15); color:#10b981; border:1px solid rgba(78, 222, 163, 0.4); padding:3px 7px; border-radius:5px; font-size:0.7rem; font-weight:700;">&#x25CF; ONLINE</span><span style="display:inline-flex; align-items:center; background:rgba(96, 165, 250, 0.15); color:{title_color}; border:1px solid rgba(96, 165, 250, 0.3); padding:3px 7px; border-radius:5px; font-size:0.7rem; font-weight:700;">YOLOv8 ENGINE</span></div></div>'

def render_status_card(state_type: str, title: str, message: str, is_dark: bool = True, personnel_count: int = 1) -> str:
    """Genera la tarjeta semáforo de estado compacta para el pie de página."""
    bg_card = "#171f33" if is_dark else "#ffffff"
    border_card = "#424754" if is_dark else "#cbd5e1"
    text_primary = "#f8fafc" if is_dark else "#0f172a"
    text_muted = "#cbd5e1" if is_dark else "#475569"

    if state_type == "safe":
        status_color = "#10b981" if not is_dark else "#4edea3"
        status_bg = "rgba(78, 222, 163, 0.15)"
        status_border = "rgba(78, 222, 163, 0.4)"
        icon_symbol = "[OK]"
    elif state_type == "danger":
        status_color = "#ef4444" if not is_dark else "#ffb4ab"
        status_bg = "rgba(255, 180, 171, 0.18)"
        status_border = "rgba(255, 180, 171, 0.5)"
        icon_symbol = "[!]"
    else:  # standby
        status_color = "#3b82f6" if not is_dark else "#adc6ff"
        status_bg = "rgba(173, 198, 255, 0.15)"
        status_border = "rgba(173, 198, 255, 0.35)"
        icon_symbol = "[--]"

    return f'<div style="background-color:{bg_card}; border:1px solid {status_border}; border-radius:8px; padding:6px 14px; min-height:58px; display:flex; align-items:center; justify-content:space-between; gap:12px;"><div style="display:flex; align-items:center; gap:10px;"><div style="font-size:14px; font-weight:800; font-family:monospace; color:{status_color};">{icon_symbol}</div><div><div style="font-size:0.92rem; font-weight:800; color:{status_color}; line-height:1.2;">{title}</div><div style="font-size:0.73rem; color:{text_muted}; margin-top:2px;">{message}</div></div></div><div style="border-left:1px solid {border_card}; padding-left:12px; text-align:right;"><div style="font-size:0.62rem; color:{text_muted}; font-weight:700; text-transform:uppercase;">EN ESCENA</div><div style="font-size:1.15rem; font-weight:800; color:{text_primary}; line-height:1.1;">{personnel_count}</div></div></div>'

def render_incident_card(timestamp: str, title: str, badge_type: str = "danger", is_dark: bool = True) -> str:
    """Genera una tarjeta de incidente limpia y compacta para el panel lateral."""
    bg_card = "#0b1326" if is_dark else "#f1f5f9"
    border_card = "#424754" if is_dark else "#cbd5e1"
    text_primary = "#f8fafc" if is_dark else "#0f172a"
    text_muted = "#94a3b8" if is_dark else "#64748b"

    if badge_type == "danger":
        badge_bg = "rgba(239, 68, 68, 0.15)"
        badge_color = "#ef4444" if not is_dark else "#ffb4ab"
        badge_border = "rgba(239, 68, 68, 0.4)"
        icon = "[!]"
    elif badge_type == "warning":
        badge_bg = "rgba(245, 158, 11, 0.15)"
        badge_color = "#f59e0b" if not is_dark else "#ffb95f"
        badge_border = "rgba(245, 158, 11, 0.4)"
        icon = "[W]"
    else:
        badge_bg = "rgba(16, 185, 129, 0.15)"
        badge_color = "#10b981" if not is_dark else "#4edea3"
        badge_border = "rgba(16, 185, 129, 0.4)"
        icon = "[OK]"

    return f'<div style="background-color:{bg_card}; border:1px solid {border_card}; border-radius:8px; padding:8px 12px; margin-bottom:8px;"><div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:3px;"><span style="font-size:0.68rem; color:{text_muted}; font-family:monospace; font-weight:600;">{icon} {timestamp}</span><span style="font-size:0.65rem; font-weight:700; background:{badge_bg}; color:{badge_color}; border:1px solid {badge_border}; padding:1px 6px; border-radius:4px; text-transform:uppercase;">{badge_type}</span></div><div style="font-size:0.82rem; font-weight:700; color:{text_primary}; line-height:1.2;">{title}</div></div>'


