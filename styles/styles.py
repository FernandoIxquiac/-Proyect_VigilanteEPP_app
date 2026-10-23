from __future__ import annotations
import base64
from pathlib import Path
from typing import Union, Optional
import streamlit as st
from .icons import get_svg_icon, get_svg_data_uri



def _get_logo_base64() -> str:
    """Carga assets/logo.svg o assets/logo.jpg en Base64 para incrustarlo limpio en el header."""
    svg_path = Path("assets/logo.svg")
    jpg_path = Path("assets/logo.jpg")
    if svg_path.exists():
        b64 = base64.b64encode(svg_path.read_bytes()).decode("utf-8")
        return f"data:image/svg+xml;base64,{b64}"
    if jpg_path.exists():
        b64 = base64.b64encode(jpg_path.read_bytes()).decode("utf-8")
        return f"data:image/jpeg;base64,{b64}"
    return ""


def get_theme_css(is_dark: bool = True, is_mini: bool = False) -> str:
    """Genera el sistema de diseño CSS basado en variables semánticas sobrias y modo de riel."""
    uri_demo = get_svg_data_uri("device-desktop")
    uri_live = get_svg_data_uri("video")
    uri_stats = get_svg_data_uri("chart-bar")
    uri_reports = get_svg_data_uri("file-text")
    uri_settings = get_svg_data_uri("settings")
    uri_toggle = get_svg_data_uri("chevrons-left")

    if is_mini:
        sidebar_width = "72px"
        sidebar_padding = "8px"
        button_justify = "center"
        button_padding = "10px 0"
        icon_margin_right = "0"
        toggle_transform = "transform: rotate(180deg) !important;"
        mini_hide_text = ".stSidebar .stButton button p { display: none !important; }"
        mini_hide_captions = '.stSidebar div[data-testid="stCaptionContainer"], .sidebar-text-hide { display: none !important; }'
        logo_max_width = "42px"
    else:
        sidebar_width = "250px"
        sidebar_padding = "12px"
        button_justify = "flex-start"
        button_padding = "10px 14px"
        icon_margin_right = "10px"
        toggle_transform = ""
        mini_hide_text = ""
        mini_hide_captions = ""
        logo_max_width = "100%"

    if is_dark:
        vars_css = """
        --bg-app: #0B111E;
        --bg-panel: #111827;
        --bg-card: #161F30;
        --bg-elevated: #1E293B;
        --border-subtle: #26334D;
        --border-strong: #334155;
        --text-primary: #F8FAFC;
        --text-secondary: #CBD5E1;
        --text-muted: #94A3B8;
        --brand-primary: #00A8E8;
        --brand-primary-soft: rgba(0, 168, 232, 0.14);
        --shadow-card: 0 2px 8px rgba(0, 0, 0, 0.28);
        """
    else:
        vars_css = """
        --bg-app: #F4F6F9;
        --bg-panel: #FFFFFF;
        --bg-card: #FFFFFF;
        --bg-elevated: #F1F5F9;
        --border-subtle: #E2E8F0;
        --border-strong: #CBD5E1;
        --text-primary: #0F172A;
        --text-secondary: #475569;
        --text-muted: #64748B;
        --brand-primary: #0284C7;
        --brand-primary-soft: rgba(2, 132, 199, 0.10);
        --shadow-card: 0 1px 4px rgba(15, 23, 42, 0.06);
        """

    return f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600;700&display=swap');

    :root {{
        {vars_css}
        --status-safe: #10B981;
        --status-warning: #F59E0B;
        --status-danger: #EF4444;
        --status-standby: #00A8E8;
        --radius-sm: 6px;
        --radius-md: 8px;
        --radius-lg: 10px;
    }}

    /* 1. Contenedor Principal (Cockpit Ejecutivo Sobrio) */
    .block-container {{
        max-width: 1260px !important;
        padding-top: 0.75rem !important;
        padding-bottom: 1.25rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
    }}

    /* 2. Fondo y Tipografía Base (Sin romper componentes hijos en el DOM) */
    .stApp {{
        background-color: var(--bg-app) !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }}

    header[data-testid="stHeader"] {{
        background: transparent !important;
        height: 1.75rem !important;
    }}

    /* Tipografía de encabezados y párrafos limpios */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 {{
        color: var(--text-primary) !important;
        font-weight: 700 !important;
        letter-spacing: -0.01em !important;
    }}
    .stMarkdown p {{
        color: var(--text-primary) !important;
    }}

    /* Labels de Widgets (Generales) */
    label[data-testid="stWidgetLabel"],
    label[data-testid="stWidgetLabel"] *,
    label[data-testid="stWidgetLabel"] p,
    label[data-testid="stWidgetLabel"] span {{
        color: var(--text-primary) !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
    }}

    /* Textos Secundarios y Captions Globales */
    div[data-testid="stCaptionContainer"],
    div[data-testid="stCaptionContainer"] p,
    div[data-testid="stCaptionContainer"] *,
    .stCaption,
    .stCaption p,
    .stCaption *,
    small {{
        color: var(--text-secondary) !important;
        font-size: 0.82rem !important;
    }}

    /* Radio Buttons (Globales, Horizontales y Verticales) */
    div[data-testid="stRadio"] label,
    div[role="radiogroup"] label {{
        color: var(--text-primary) !important;
        cursor: pointer !important;
    }}
    div[data-testid="stRadio"] label *,
    div[data-testid="stRadio"] label p,
    div[data-testid="stRadio"] label div,
    div[data-testid="stRadio"] label span,
    div[role="radiogroup"] label *,
    div[role="radiogroup"] label p,
    div[role="radiogroup"] label span,
    div[role="radiogroup"] * {{
        color: var(--text-primary) !important;
        font-weight: 500 !important;
    }}
    div[data-testid="stRadio"] label[data-baseweb="radio"]:hover,
    div[data-testid="stRadio"] label[data-baseweb="radio"]:hover * {{
        color: var(--brand-primary) !important;
    }}

    /* Widget Labels (Checkboxes y Toggles) */
    div[data-testid="stCheckbox"] label,
    div[data-testid="stCheckbox"] label *,
    div[data-testid="stCheckbox"] label p,
    div[data-testid="stCheckbox"] label span,
    div[data-testid="stToggle"] label,
    div[data-testid="stToggle"] label *,
    div[data-testid="stToggle"] label p,
    div[data-testid="stToggle"] label span {{
        color: var(--text-primary) !important;
        font-weight: 500 !important;
    }}

    /* Borde sobrio de contraste para toggles y checkboxes en modales y temas claros */
    div[data-testid="stToggle"] div[data-baseweb="toggle"],
    div[data-testid="stToggle"] span[data-baseweb="toggle"],
    div[data-testid="stToggle"] [data-baseweb="toggle"] {{
        border: 1.5px solid var(--border-strong) !important;
    }}

    /* Sliders Globales */
    div[data-testid="stSlider"],
    div[data-testid="stSlider"] *,
    div[data-testid="stSlider"] p,
    div[data-testid="stSlider"] span,
    div[data-testid="stSlider"] div,
    div[data-baseweb="slider"],
    div[data-baseweb="slider"] *,
    div[data-testid="stSliderTickBar"] * {{
        color: var(--text-primary) !important;
    }}
    div[data-testid="stSliderTickBarItem"] {{
        color: var(--text-secondary) !important;
    }}

    /* Iconos de Tooltips de Ayuda (?) */
    div[data-testid="stTooltipIcon"] svg,
    div[data-testid="stTooltipIcon"] *,
    [data-testid="stTooltipHoverTarget"] * {{
        fill: var(--text-secondary) !important;
        color: var(--text-secondary) !important;
    }}

    /* Alertas del Sistema (st.info, st.warning, st.error, st.success) */
    div[data-testid="stAlert"] {{
        background-color: var(--bg-elevated) !important;
        border: 1px solid var(--border-strong) !important;
        border-left: 4px solid var(--brand-primary) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-primary) !important;
        box-shadow: var(--shadow-card) !important;
    }}
    div[data-testid="stAlert"] * {{
        color: var(--text-primary) !important;
    }}
    div[data-testid="stAlert"] p {{
        color: var(--text-primary) !important;
        font-size: 0.86rem !important;
        line-height: 1.4 !important;
    }}
    div[data-testid="stAlert"] svg {{
        fill: var(--brand-primary) !important;
        color: var(--brand-primary) !important;
    }}
    div[data-testid="stAlert"]:has([data-testid="stNotificationIconWarning"]),
    div[data-testid="stAlert"][kind="warning"] {{
        border-left-color: var(--status-warning) !important;
    }}
    div[data-testid="stAlert"]:has([data-testid="stNotificationIconWarning"]) svg,
    div[data-testid="stAlert"][kind="warning"] svg {{
        fill: var(--status-warning) !important;
        color: var(--status-warning) !important;
    }}
    div[data-testid="stAlert"]:has([data-testid="stNotificationIconError"]),
    div[data-testid="stAlert"][kind="error"] {{
        border-left-color: var(--status-danger) !important;
    }}
    div[data-testid="stAlert"]:has([data-testid="stNotificationIconError"]) svg,
    div[data-testid="stAlert"][kind="error"] svg {{
        fill: var(--status-danger) !important;
        color: var(--status-danger) !important;
    }}
    div[data-testid="stAlert"]:has([data-testid="stNotificationIconSuccess"]),
    div[data-testid="stAlert"][kind="success"] {{
        border-left-color: var(--status-safe) !important;
    }}
    div[data-testid="stAlert"]:has([data-testid="stNotificationIconSuccess"]) svg,
    div[data-testid="stAlert"][kind="success"] svg {{
        fill: var(--status-safe) !important;
        color: var(--status-safe) !important;
    }}

    /* 3. Desactivar Colapso Nativo a 0px de Streamlit */
    button[data-testid="stSidebarCollapseButton"],
    div[data-testid="collapsedControl"],
    div[data-testid="stSidebarResizeHandle"] {{
        display: none !important;
    }}

    /* 4. Sidebar Corporativo y Dimensiones del Riel Permanente */
    section[data-testid="stSidebar"] {{
        background-color: var(--bg-panel) !important;
        border-right: 1px solid var(--border-subtle) !important;
        width: {sidebar_width} !important;
        min-width: {sidebar_width} !important;
        max-width: {sidebar_width} !important;
        transition: width 0.2s ease-in-out !important;
    }}
    section[data-testid="stSidebar"] > div:first-child,
    section[data-testid="stSidebar"] div[data-testid="stSidebarContent"] {{
        width: {sidebar_width} !important;
        min-width: {sidebar_width} !important;
        max-width: {sidebar_width} !important;
        padding-left: {sidebar_padding} !important;
        padding-right: {sidebar_padding} !important;
        overflow-x: hidden !important;
        transition: width 0.2s ease-in-out !important;
    }}
    section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {{
        color: var(--text-secondary) !important;
        font-size: 0.84rem !important;
    }}
    section[data-testid="stSidebar"] * {{
        color: var(--text-primary) !important;
    }}
    .stSidebar img {{
        max-width: {logo_max_width} !important;
        margin: 0 auto !important;
        display: block !important;
        transition: max-width 0.2s ease-in-out !important;
    }}

    /* Modos reactivos del riel compacto */
    {mini_hide_text}
    {mini_hide_captions}

    /* 5. Anclas de Navegacion Invisibles */
    div[data-testid="stElementContainer"]:has(.nav-anchor),
    div[data-testid="stVerticalBlock"] > div:has(.nav-anchor) {{
        height: 0 !important;
        min-height: 0 !important;
        margin: 0 !important;
        padding: 0 !important;
        overflow: hidden !important;
    }}

    /* 6. Botones de Navegacion en Sidebar */
    .stSidebar .stButton {{
        width: 100% !important;
        margin-bottom: 2px !important;
    }}
    .stSidebar .stButton > button {{
        width: 100% !important;
        border-radius: var(--radius-sm) !important;
        min-height: 40px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        letter-spacing: 0.01em !important;
        transition: all 0.15s ease-in-out !important;
        display: flex !important;
        align-items: center !important;
        justify-content: {button_justify} !important;
        padding: {button_padding} !important;
    }}

    /* Heredar color en etiquetas de texto de botones del sidebar */
    .stSidebar .stButton button p,
    .stSidebar .stButton button span {{
        color: inherit !important;
        font-weight: 600 !important;
    }}

    /* Boton Primario (Activo en Navegacion) */
    .stSidebar .stButton > button[kind="primary"],
    .stSidebar .stButton > button[data-testid="stBaseButton-primary"] {{
        background-color: var(--brand-primary) !important;
        border: 1px solid transparent !important;
        color: #FFFFFF !important;
        box-shadow: 0 2px 6px rgba(0, 168, 232, 0.28) !important;
    }}
    .stSidebar .stButton > button[kind="primary"] *,
    .stSidebar .stButton > button[data-testid="stBaseButton-primary"] * {{
        color: #FFFFFF !important;
    }}
    .stSidebar .stButton > button[kind="primary"]:hover,
    .stSidebar .stButton > button[data-testid="stBaseButton-primary"]:hover {{
        background-color: var(--brand-primary) !important;
        border-color: transparent !important;
        color: #FFFFFF !important;
        opacity: 0.92 !important;
        box-shadow: 0 2px 6px rgba(0, 168, 232, 0.35) !important;
    }}

    /* Forzar texto blanco en botones activos del sidebar con maxima especificidad */
    section[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] p,
    section[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"] span,
    section[data-testid="stSidebar"] button[kind="primary"] p,
    section[data-testid="stSidebar"] button[kind="primary"] span {{
        color: #FFFFFF !important;
    }}

    /* Boton Secundario (Inactivo en Navegacion - Diseno Minimalista Ghost / Flat) */
    .stSidebar .stButton > button[kind="secondary"],
    .stSidebar .stButton > button[data-testid="stBaseButton-secondary"],
    .stSidebar .stButton > button:not([kind="primary"]):not([data-testid="stBaseButton-primary"]) {{
        background-color: transparent !important;
        border: 1px solid transparent !important;
        color: var(--text-secondary) !important;
        box-shadow: none !important;
    }}
    .stSidebar .stButton > button[kind="secondary"] *,
    .stSidebar .stButton > button[data-testid="stBaseButton-secondary"] *,
    .stSidebar .stButton > button:not([kind="primary"]):not([data-testid="stBaseButton-primary"]) * {{
        color: inherit !important;
    }}
    .stSidebar .stButton > button[kind="secondary"]:hover,
    .stSidebar .stButton > button[data-testid="stBaseButton-secondary"]:hover,
    .stSidebar .stButton > button:not([kind="primary"]):not([data-testid="stBaseButton-primary"]):hover {{
        background-color: var(--brand-primary-soft) !important;
        border-color: transparent !important;
        color: var(--brand-primary) !important;
    }}
    .stSidebar .stButton > button[kind="secondary"]:hover *,
    .stSidebar .stButton > button[data-testid="stBaseButton-secondary"]:hover *,
    .stSidebar .stButton > button:not([kind="primary"]):not([data-testid="stBaseButton-primary"]):hover * {{
        color: inherit !important;
    }}

    /* 7. Iconos SVG en Botones via CSS Mask */
    .stSidebar .stButton button::before {{
        content: '';
        display: inline-block;
        width: 18px;
        height: 18px;
        flex-shrink: 0;
        background-color: currentColor;
        -webkit-mask-size: contain;
        mask-size: contain;
        -webkit-mask-repeat: no-repeat;
        mask-repeat: no-repeat;
        -webkit-mask-position: center;
        mask-position: center;
        margin-right: {icon_margin_right} !important;
    }}

    div[data-testid="stElementContainer"]:has(.nav-anchor[data-nav="demo"]) + div[data-testid="stElementContainer"] .stButton button::before,
    div[data-testid="stVerticalBlock"] > div:has(.nav-anchor[data-nav="demo"]) + div .stButton button::before {{
        -webkit-mask-image: url('{uri_demo}') !important;
        mask-image: url('{uri_demo}') !important;
    }}

    div[data-testid="stElementContainer"]:has(.nav-anchor[data-nav="live"]) + div[data-testid="stElementContainer"] .stButton button::before,
    div[data-testid="stVerticalBlock"] > div:has(.nav-anchor[data-nav="live"]) + div .stButton button::before {{
        -webkit-mask-image: url('{uri_live}') !important;
        mask-image: url('{uri_live}') !important;
    }}

    div[data-testid="stElementContainer"]:has(.nav-anchor[data-nav="stats"]) + div[data-testid="stElementContainer"] .stButton button::before,
    div[data-testid="stVerticalBlock"] > div:has(.nav-anchor[data-nav="stats"]) + div .stButton button::before {{
        -webkit-mask-image: url('{uri_stats}') !important;
        mask-image: url('{uri_stats}') !important;
    }}

    div[data-testid="stElementContainer"]:has(.nav-anchor[data-nav="reports"]) + div[data-testid="stElementContainer"] .stButton button::before,
    div[data-testid="stVerticalBlock"] > div:has(.nav-anchor[data-nav="reports"]) + div .stButton button::before {{
        -webkit-mask-image: url('{uri_reports}') !important;
        mask-image: url('{uri_reports}') !important;
    }}

    div[data-testid="stElementContainer"]:has(.nav-anchor[data-nav="settings"]) + div[data-testid="stElementContainer"] .stButton button::before,
    div[data-testid="stVerticalBlock"] > div:has(.nav-anchor[data-nav="settings"]) + div .stButton button::before {{
        -webkit-mask-image: url('{uri_settings}') !important;
        mask-image: url('{uri_settings}') !important;
    }}

    div[data-testid="stElementContainer"]:has(.nav-anchor[data-nav="toggle"]) + div[data-testid="stElementContainer"] .stButton button::before,
    div[data-testid="stVerticalBlock"] > div:has(.nav-anchor[data-nav="toggle"]) + div .stButton button::before {{
        -webkit-mask-image: url('{uri_toggle}') !important;
        mask-image: url('{uri_toggle}') !important;
        {toggle_transform}
    }}

    /* Compatibilidad con Radio Buttons en Sidebar (si existieran) */
    .stSidebar .stRadio > div {{ gap: 6px; }}
    .stSidebar .stRadio label {{
        padding: 9px 14px;
        border-radius: var(--radius-md);
        cursor: pointer;
        font-weight: 600;
        font-size: 0.88rem;
        color: var(--text-primary) !important;
        border: 1px solid transparent;
        transition: all 0.15s ease-in-out;
    }}
    .stSidebar .stRadio label:hover {{
        background: var(--brand-primary-soft);
        border-color: var(--border-subtle);
        color: var(--brand-primary) !important;
    }}
    .stSidebar .stRadio label span,
    .stSidebar .stRadio label p,
    .stSidebar .stRadio label * {{
        color: var(--text-primary) !important;
        letter-spacing: 0.01em;
    }}

    /* 5. Tarjetas de Métricas Nativas (st.metric) */
    div[data-testid="stMetric"] {{
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-top: 2px solid var(--brand-primary) !important;
        padding: 10px 14px !important;
        border-radius: var(--radius-md) !important;
        box-shadow: var(--shadow-card) !important;
    }}
    div[data-testid="stMetricLabel"],
    div[data-testid="stMetricLabel"] *,
    div[data-testid="stMetricLabel"] label,
    div[data-testid="stMetricLabel"] p,
    div[data-testid="stMetricLabel"] span,
    div[data-testid="stMetricLabel"] div {{
        color: var(--text-secondary) !important;
        font-size: 0.72rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.04em !important;
    }}
    div[data-testid="stMetricValue"],
    div[data-testid="stMetricValue"] *,
    div[data-testid="stMetricValue"] div {{
        color: var(--text-primary) !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 1.35rem !important;
        font-weight: 700 !important;
        font-variant-numeric: tabular-nums !important;
    }}
    div[data-testid="stMetricDelta"],
    div[data-testid="stMetricDelta"] *,
    div[data-testid="stMetricDelta"] div,
    div[data-testid="stMetricDelta"] span {{
        font-size: 0.72rem !important;
        font-weight: 600 !important;
    }}

    /* 6. Visor de Cámara e Imágenes */
    div[data-testid="stImage"] img {{
        max-height: 440px !important;
        width: 100% !important;
        object-fit: contain !important;
        background-color: #050811 !important;
        border-radius: var(--radius-md) !important;
        border: 1px solid var(--border-strong) !important;
        box-shadow: var(--shadow-card) !important;
    }}

    /* 7. Inputs, Selectbox y Menús Flotantes (BaseWeb Fix) */
    div[data-baseweb="select"] > div,
    div[data-testid="stTextInput"] input,
    div[data-testid="stNumberInput"] input {{
        background-color: var(--bg-card) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-strong) !important;
        border-radius: var(--radius-sm) !important;
        font-size: 0.85rem !important;
    }}
    div[data-baseweb="select"] *,
    div[data-baseweb="select"] div,
    div[data-baseweb="select"] span,
    div[data-baseweb="select"] input {{
        color: var(--text-primary) !important;
    }}
    div[data-baseweb="select"] svg {{
        fill: var(--text-secondary) !important;
    }}
    div[data-baseweb="popover"] ul,
    ul[data-testid="stSelectboxVirtualDropdown"] {{
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border-strong) !important;
    }}
    li[data-testid="stSelectboxVirtualDropdown-item"] {{
        color: var(--text-primary) !important;
        font-size: 0.85rem !important;
    }}
    li[data-testid="stSelectboxVirtualDropdown-item"]:hover {{
        background-color: var(--brand-primary-soft) !important;
        color: var(--brand-primary) !important;
    }}

    /* 8. Botones Primarios y Secundarios */
    .stButton > button, div[data-testid="stDownloadButton"] > button {{
        border-radius: var(--radius-sm) !important;
        font-weight: 600 !important;
        font-size: 0.84rem !important;
        padding: 0.4rem 1rem !important;
        transition: all 0.15s ease !important;
    }}
    button[kind="primary"] {{
        background-color: var(--brand-primary) !important;
        color: #FFFFFF !important;
        border: 1px solid var(--brand-primary) !important;
    }}
    button[kind="secondary"] {{
        background-color: var(--bg-card) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-strong) !important;
    }}
    button[kind="secondary"]:hover {{
        border-color: var(--brand-primary) !important;
        color: var(--brand-primary) !important;
        background-color: var(--brand-primary-soft) !important;
    }}

    /* 9. File Uploader Compacto y Sobrio */
    section[data-testid="stFileUploaderDropzone"] {{
        background-color: var(--bg-card) !important;
        border: 1px dashed var(--border-strong) !important;
        border-radius: var(--radius-md) !important;
        padding: 14px 20px !important;
    }}
    section[data-testid="stFileUploaderDropzone"]:hover {{
        border-color: var(--brand-primary) !important;
        background-color: var(--bg-elevated) !important;
    }}
    div[data-testid="stFileUploader"] {{
        background-color: transparent !important;
    }}
    div[data-testid="stFileUploaderDropzone"] *,
    section[data-testid="stFileUploaderDropzone"] * {{
        color: var(--text-primary) !important;
    }}
    div[data-testid="stFileUploaderDropzone"] small,
    section[data-testid="stFileUploaderDropzone"] small {{
        color: var(--text-muted) !important;
        font-size: 0.78rem !important;
    }}
    div[data-testid="stFileUploaderDropzone"] svg,
    section[data-testid="stFileUploaderDropzone"] svg {{
        fill: var(--brand-primary) !important;
    }}
    div[data-testid="stFileUploaderDropzone"] button,
    section[data-testid="stFileUploaderDropzone"] button {{
        background-color: var(--bg-elevated) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-strong) !important;
        border-radius: var(--radius-sm) !important;
        font-weight: 600 !important;
        padding: 6px 16px !important;
    }}
    div[data-testid="stFileUploaderDropzone"] button:hover,
    section[data-testid="stFileUploaderDropzone"] button:hover {{
        border-color: var(--brand-primary) !important;
        color: var(--brand-primary) !important;
    }}
    div[data-testid="stFileUploaderFileData"] {{
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border-strong) !important;
        border-radius: var(--radius-sm) !important;
        padding: 8px 12px !important;
    }}
    div[data-testid="stFileUploaderFileData"] * {{
        color: var(--text-primary) !important;
    }}
    div[data-testid="stFileUploaderDeleteBtn"] button {{
        color: var(--text-muted) !important;
    }}
    div[data-testid="stFileUploaderDeleteBtn"] button:hover {{
        color: #ef4444 !important;
    }}

    /* 10. Expanders y Tablas */
    div[data-testid="stExpander"],
    details[data-testid="stExpander"],
    details {{
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-md) !important;
        margin-top: 6px !important;
        margin-bottom: 6px !important;
    }}
    details[data-testid="stExpander"] summary,
    div[data-testid="stExpander"] summary,
    summary[data-testid="stExpanderToggle"],
    details summary {{
        background-color: var(--bg-card) !important;
        color: var(--text-primary) !important;
        border-radius: var(--radius-md) !important;
        padding: 8px 14px !important;
        font-weight: 600 !important;
        border: none !important;
    }}
    details[data-testid="stExpander"] summary:hover,
    div[data-testid="stExpander"] summary:hover,
    summary[data-testid="stExpanderToggle"]:hover,
    details summary:hover {{
        background-color: var(--bg-elevated) !important;
        color: var(--brand-primary) !important;
    }}
    details summary p, details summary span, details summary div {{
        color: var(--text-primary) !important;
        font-weight: 600 !important;
    }}
    details summary svg {{
        fill: var(--text-primary) !important;
    }}
    div[data-testid="stExpanderDetails"] {{
        background-color: var(--bg-card) !important;
        color: var(--text-primary) !important;
        border-top: 1px solid var(--border-subtle) !important;
        padding: 12px !important;
        border-bottom-left-radius: var(--radius-md) !important;
        border-bottom-right-radius: var(--radius-md) !important;
    }}
    div[data-testid="stExpanderDetails"] * {{
        color: var(--text-primary) !important;
    }}
    div[data-testid="stDataFrame"] {{
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-md) !important;
        padding: 4px !important;
    }}

    /* Vega-Lite Charts (st.bar_chart / st.line_chart) */
    div[data-testid="stArrowVegaLiteChart"] {{
        background-color: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-radius: var(--radius-md) !important;
        padding: 12px !important;
    }}
    div[data-testid="stArrowVegaLiteChart"] svg,
    div[data-testid="stArrowVegaLiteChart"] .vega-embed {{
        background-color: transparent !important;
    }}
    div[data-testid="stArrowVegaLiteChart"] text {{
        fill: var(--text-secondary) !important;
    }}
    div[data-testid="stArrowVegaLiteChart"] line {{
        stroke: var(--border-strong) !important;
    }}

    /* 15. Modal de Configuracion - Compacto y Dark/Light Theme Completo */
    div[data-testid="stDialog"] {{
        padding: 1.2rem 1.5rem !important;
    }}
    div[data-testid="stDialog"] div[data-testid="stVerticalBlock"],
    div[role="dialog"] div[data-testid="stVerticalBlock"] {{
        gap: 0.45rem !important;
    }}
    div[data-testid="stDialog"] > div,
    div[role="dialog"],
    div[data-testid="stModal"] > div,
    div[data-modal="true"] {{
        background-color: var(--bg-panel) !important;
        color: var(--text-primary) !important;
        border: 1px solid var(--border-strong) !important;
        border-radius: var(--radius-lg) !important;
        box-shadow: 0 10px 35px rgba(0, 0, 0, 0.45) !important;
    }}
    div[data-testid="stDialogHeader"],
    div[role="dialog"] header,
    div[data-testid="stDialog"] header {{
        background-color: var(--bg-panel) !important;
        color: var(--text-primary) !important;
        border-bottom: 1px solid var(--border-subtle) !important;
        padding-bottom: 0.5rem !important;
    }}
    .stDialogBody,
    div[data-testid="stDialog"] .stDialogBody,
    div[role="dialog"] .stDialogBody,
    div[data-testid="stDialog"] [data-testid="stVerticalBlock"],
    div[role="dialog"] [data-testid="stVerticalBlock"] {{
        background-color: var(--bg-panel) !important;
        color: var(--text-primary) !important;
    }}
    div[role="dialog"] h1, div[role="dialog"] h2, div[role="dialog"] h3, div[role="dialog"] h4,
    div[data-testid="stDialog"] h1, div[data-testid="stDialog"] h2, div[data-testid="stDialog"] h3, div[data-testid="stDialog"] h4,
    div[data-testid="stModal"] h1, div[data-testid="stModal"] h2, div[data-testid="stModal"] h3, div[data-testid="stModal"] h4 {{
        color: var(--text-primary) !important;
        font-weight: 700 !important;
    }}
    div[role="dialog"] p, div[data-testid="stDialog"] p, div[data-testid="stModal"] p,
    div[role="dialog"] label, div[data-testid="stDialog"] label, div[data-testid="stModal"] label,
    div[role="dialog"] span, div[data-testid="stDialog"] span, div[data-testid="stModal"] span {{
        color: var(--text-primary) !important;
    }}
    div[role="dialog"] small, div[data-testid="stDialog"] small,
    div[role="dialog"] caption, div[data-testid="stDialog"] [data-testid="stCaptionContainer"] p {{
        color: var(--text-secondary) !important;
    }}
    div[role="dialog"] .stCheckbox label span,
    div[data-testid="stDialog"] .stCheckbox label span,
    div[role="dialog"] .stToggle label p,
    div[data-testid="stDialog"] .stToggle label p,
    div[role="dialog"] .stSlider label span,
    div[data-testid="stDialog"] .stSlider label span,
    div[role="dialog"] [data-testid="stMarkdownContainer"] p,
    div[data-testid="stDialog"] [data-testid="stMarkdownContainer"] p {{
        color: var(--text-primary) !important;
        font-weight: 600 !important;
    }}
    div[role="dialog"] [data-testid="stInfo"],
    div[data-testid="stDialog"] [data-testid="stInfo"],
    div[data-testid="stModal"] [data-testid="stInfo"] {{
        background-color: var(--bg-elevated) !important;
        border: 1px solid var(--border-subtle) !important;
        border-left: 4px solid var(--brand-primary) !important;
        border-radius: var(--radius-sm) !important;
    }}
    div[role="dialog"] [data-testid="stInfo"] *,
    div[data-testid="stDialog"] [data-testid="stInfo"] * {{
        color: var(--text-primary) !important;
    }}
    div[role="dialog"] hr,
    div[data-testid="stDialog"] hr,
    div[data-testid="stModal"] hr {{
        border-color: var(--border-subtle) !important;
    }}
    div[role="dialog"] button[aria-label="Close"],
    div[data-testid="stDialog"] button[aria-label="Close"],
    [data-testid="stDialogCloseButton"] {{
        color: var(--text-primary) !important;
        background-color: transparent !important;
    }}
    div[role="dialog"] button[kind="primary"] *,
    div[data-testid="stDialog"] button[kind="primary"] * {{
        color: #FFFFFF !important;
    }}
    div[role="dialog"] button[kind="secondary"] *,
    div[data-testid="stDialog"] button[kind="secondary"] * {{
        color: var(--text-primary) !important;
    }}
    [data-testid="stDialogOverlay"],
    [data-testid="stModalOverlay"],
    div[data-testid="stModal"] > div:first-child {{
        background-color: rgba(0, 0, 0, 0.65) !important;
        backdrop-filter: blur(2px) !important;
    }}

    /* Clases utilitarias semanticas de diseno industrial */
    .section-header {{
        font-size: 0.75rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.04em !important;
        color: var(--text-secondary) !important;
        margin-bottom: 4px !important;
    }}

    .preset-hint {{
        font-size: 0.72rem !important;
        color: var(--text-secondary) !important;
        margin: 4px 0 2px 0 !important;
    }}

    .feed-header {{
        font-size: 0.75rem !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.04em !important;
        color: var(--brand-primary) !important;
        margin-bottom: 6px !important;
    }}

    .status-indicator-stopped {{
        text-align: center !important;
        font-size: 0.78rem !important;
        font-weight: 700 !important;
        color: var(--text-secondary) !important;
        margin-top: 4px !important;
    }}

    .status-indicator-running {{
        text-align: center !important;
        font-size: 0.78rem !important;
        font-weight: 700 !important;
        color: var(--status-safe) !important;
        margin-top: 4px !important;
    }}

    .hud-card {{
        background: var(--bg-card) !important;
        border: 1px solid var(--border-subtle) !important;
        border-left: 5px solid var(--brand-primary) !important;
        border-radius: var(--radius-md) !important;
        padding: 28px 20px !important;
        text-align: center !important;
        box-shadow: var(--shadow-card) !important;
    }}

    .hud-card-title {{
        font-size: 1.15rem !important;
        font-weight: 800 !important;
        color: var(--brand-primary) !important;
        margin-bottom: 8px !important;
    }}

    .hud-card-desc {{
        font-size: 0.88rem !important;
        color: var(--text-secondary) !important;
        max-width: 520px !important;
        margin: 0 auto !important;
        line-height: 1.45 !important;
    }}

    .layout-spacer {{
        margin-top: 8px !important;
        margin-bottom: 8px !important;
    }}

    .badge-indicator {{
        display: inline-flex !important;
        align-items: center !important;
        gap: 4px !important;
        font-size: 0.68rem !important;
        font-weight: 800 !important;
        padding: 2px 8px !important;
        border-radius: 4px !important;
    }}

    .kpi-subtext {{
        font-size: 0.80rem !important;
        color: var(--text-secondary) !important;
        line-height: 1.3 !important;
    }}
</style>
"""


def apply_styles(theme_mode: bool | str = True, is_mini: bool = False) -> None:
    """Inyecta las variables y estilos CSS según el modo activo y dimensiones del riel."""
    if theme_mode is not None:
        is_dark = theme_mode if isinstance(theme_mode, bool) else ("Oscuro" in str(theme_mode) or "Dark" in str(theme_mode))
    elif "config" in st.session_state and "is_dark" in st.session_state.config:
        is_dark = st.session_state.config["is_dark"]
    else:
        is_dark = st.session_state.get("is_dark", True)

    if not is_mini and "sidebar_mini" in st.session_state:
        is_mini = st.session_state["sidebar_mini"]

    st.markdown(get_theme_css(is_dark=is_dark, is_mini=is_mini), unsafe_allow_html=True)


def render_top_header(is_dark: bool = True) -> str:
    """Barra superior institucional con el escudo oficial de Vigilante EPP."""
    logo_src = _get_logo_base64()
    logo_html = (
        f'<img src="{logo_src}" style="height:36px; width:auto; border-radius:4px; object-fit:contain;" alt="Logo"/>'
        if logo_src
        else '<div style="font-family:\'JetBrains Mono\',monospace; font-weight:800; font-size:13px; color:var(--brand-primary); background:var(--brand-primary-soft); border:1px solid var(--brand-primary); padding:4px 8px; border-radius:6px;">EPP</div>'
    )
    icon_active = get_svg_icon("shield-check", size=13, color="#10B981", stroke_width=2.2)
    icon_cpu = get_svg_icon("cpu", size=13, color="var(--text-secondary)", stroke_width=2.0)

    return (
        f'<div style="display:flex; justify-content:space-between; align-items:center; '
        f'background-color:var(--bg-card); border:1px solid var(--border-subtle); border-radius:8px; padding:8px 16px; margin-bottom:10px; box-shadow:var(--shadow-card);">'
        f'<div style="display:flex; align-items:center; gap:12px;">'
        f'{logo_html}'
        f'<div>'
        f'<div style="display:flex; align-items:baseline; gap:8px;">'
        f'<span style="font-size:1.02rem; font-weight:800; color:var(--text-primary); letter-spacing:0.03em;">VIGILANTE EPP</span>'
        f'<span style="font-size:0.74rem; font-family:\'JetBrains Mono\',monospace; font-weight:600; color:var(--brand-primary);">v4.0</span>'
        f'</div>'
        f'<div style="font-size:0.72rem; color:var(--text-secondary);">Monitoreo Inteligente de Seguridad Industrial en Tiempo Real</div>'
        f'</div></div>'
        f'<div style="display:flex; align-items:center; gap:8px;">'
        f'<span style="display:inline-flex; align-items:center; gap:6px; background:rgba(16,185,129,0.12); color:#10B981; border:1px solid rgba(16,185,129,0.35); padding:3px 9px; border-radius:6px; font-size:0.68rem; font-family:\'JetBrains Mono\',monospace; font-weight:600;">{icon_active} SISTEMA ACTIVO</span>'
        f'<span style="display:inline-flex; align-items:center; gap:6px; background:var(--bg-elevated); color:var(--text-secondary); border:1px solid var(--border-strong); padding:3px 9px; border-radius:6px; font-size:0.68rem; font-family:\'JetBrains Mono\',monospace; font-weight:600;">{icon_cpu} YOLOv8 + ByteTrack</span>'
        f'</div></div>'
    )


def render_status_card(state_type: str, title: str, message: str, is_dark: bool = True, personnel_count: int = 0) -> str:
    """Tarjeta Semáforo ISO 3864 con soporte completo para: safe, warning, danger y standby."""
    palette = {
        "safe":    {"color": "#10B981", "bg": "rgba(16, 185, 129, 0.10)", "border": "rgba(16, 185, 129, 0.40)", "label": "SEGURO", "icon": "shield-check"},
        "warning": {"color": "#F59E0B", "bg": "rgba(245, 158, 11, 0.10)", "border": "rgba(245, 158, 11, 0.40)", "label": "ADVERTENCIA", "icon": "alert-triangle"},
        "danger":  {"color": "#EF4444", "bg": "rgba(239, 68, 68, 0.12)",  "border": "rgba(239, 68, 68, 0.45)",  "label": "CRÍTICO", "icon": "shield-x"},
        "standby": {"color": "#00A8E8", "bg": "rgba(0, 168, 232, 0.10)",  "border": "rgba(0, 168, 232, 0.35)",  "label": "EN ESPERA", "icon": "clock"},
    }
    cfg = palette.get(state_type, palette["standby"])
    status_icon = get_svg_icon(cfg["icon"], size=14, color=cfg["color"], stroke_width=2.2)

    return (
        f'<div style="background-color:var(--bg-card); border:2px solid {cfg["border"]}; border-radius:8px; padding:10px 14px; min-height:64px; '
        f'display:flex; align-items:center; justify-content:space-between; gap:12px; box-shadow:var(--shadow-card);">'
        f'<div style="display:flex; flex-direction:column; gap:2px;">'
        f'<div style="display:flex; align-items:center; gap:8px;">'
        f'<span style="display:inline-flex; align-items:center; gap:5px; font-size:0.65rem; font-family:\'JetBrains Mono\',monospace; font-weight:700; color:{cfg["color"]}; background:{cfg["bg"]}; padding:3px 7px; border-radius:4px;">{status_icon} {cfg["label"]}</span>'
        f'<span style="font-size:0.88rem; font-weight:700; color:var(--text-primary);">{title}</span>'
        f'</div>'
        f'<div style="font-size:0.74rem; color:var(--text-secondary);">{message}</div>'
        f'</div>'
        f'<div style="border-left:1px solid var(--border-subtle); padding-left:14px; text-align:right; min-width:72px;">'
        f'<div style="font-size:0.62rem; color:var(--text-secondary); font-weight:600; text-transform:uppercase; letter-spacing:0.04em;">Personal</div>'
        f'<div style="font-size:1.25rem; font-family:\'JetBrains Mono\',monospace; font-weight:700; color:var(--text-primary); line-height:1.15;">{personnel_count}</div>'
        f'</div></div>'
    )


def render_incident_card(timestamp: str, title: str, badge_type: str = "danger", is_dark: bool = True) -> str:
    """Tarjeta compacta de bitácora con acento lateral semántico y tipografía monoespaciada para la hora."""
    badges = {
        "danger":  {"color": "#EF4444", "bg": "rgba(239, 68, 68, 0.12)",  "border": "rgba(239, 68, 68, 0.35)",  "text": "INFRACCIÓN", "icon": "shield-x"},
        "warning": {"color": "#F59E0B", "bg": "rgba(245, 158, 11, 0.12)", "border": "rgba(245, 158, 11, 0.35)", "text": "ADVERTENCIA", "icon": "alert-triangle"},
        "safe":    {"color": "#10B981", "bg": "rgba(16, 185, 129, 0.12)", "border": "rgba(16, 185, 129, 0.35)", "text": "CUMPLIMIENTO", "icon": "shield-check"},
    }
    b = badges.get(badge_type, badges["safe"])
    b_icon = get_svg_icon(b["icon"], size=12, color=b["color"], stroke_width=2.0)

    return (
        f'<div style="background-color:var(--bg-card); border:1px solid {b["border"]}; border-radius:6px; padding:8px 12px; margin-bottom:6px;">'
        f'<div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:4px;">'
        f'<span style="font-size:0.70rem; color:var(--text-secondary); font-family:\'JetBrains Mono\',monospace; font-weight:600;">{timestamp}</span>'
        f'<span style="display:inline-flex; align-items:center; gap:4px; font-size:0.62rem; font-family:\'JetBrains Mono\',monospace; font-weight:700; background:{b["bg"]}; color:{b["color"]}; border:1px solid {b["border"]}; padding:2px 6px; border-radius:4px;">{b_icon} {b["text"]}</span>'
        f'</div>'
        f'<div style="font-size:0.80rem; font-weight:600; color:var(--text-primary); line-height:1.25;">{title}</div>'
        f'</div>'
    )
