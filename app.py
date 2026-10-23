import os
import streamlit as st

from styles import apply_styles, render_top_header, _get_logo_base64
from modules.detector import load_detector_model
from modules.metrics import init_session_state
from modules.auditor import get_live_auditor
from modules.demo_video import get_demo_video_service
from modules.camera_sources import CAMERA_OPTIONS
from modules.views import (
    config_dialog,
    render_demo_view,
    render_live_view,
    render_stats_view,
    render_reports_view,
)

st.set_page_config(
    page_title="VIGILANTE EPP - Detector Inteligente",
    page_icon="assets/logo.jpg",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_session_state()

if "config" not in st.session_state:
    st.session_state.config = {
        "is_dark": False,
        "check_helmet": True,
        "check_vest": True,
        "sensitivity_mode": "Media",
        "conf_threshold_pct": 45,
    }

for key, val in st.session_state.config.items():
    st.session_state.setdefault(key, val)

get_live_auditor().set_theme(st.session_state.config.get("is_dark", False))

if "sidebar_mini" not in st.session_state:
    st.session_state.sidebar_mini = False

if st.query_params.get("current_page") == "live":
    st.session_state.current_page = "Analisis en Vivo"
    del st.query_params["current_page"]

if "current_page" not in st.session_state:
    st.session_state.current_page = "Demostracion"
elif st.session_state.current_page not in ["Demostracion", "Analisis en Vivo", "Estadisticas", "Reportes"]:
    for valid_page in ["Demostracion", "Analisis en Vivo", "Estadisticas", "Reportes"]:
        if valid_page in st.session_state.current_page:
            st.session_state.current_page = valid_page
            break
    else:
        st.session_state.current_page = "Demostracion"

model, model_info = load_detector_model()

if st.query_params.get("view") == "monitor":
    st.session_state.current_page = "Analisis en Vivo"
    legacy_camera = st.query_params.get("camera")
    legacy_camera_choices = {
        str(index): choice
        for index, choice in enumerate(CAMERA_OPTIONS[:3])
    }
    if legacy_camera in legacy_camera_choices:
        st.session_state.camera_source_choice = legacy_camera_choices[legacy_camera]
    del st.query_params["view"]
    if "camera" in st.query_params:
        del st.query_params["camera"]

with st.sidebar:
    sidebar_logo = _get_logo_base64()
    if st.session_state.sidebar_mini:
        if sidebar_logo:
            st.markdown(
                f'<div style="text-align:center; padding:4px 0;"><img src="{sidebar_logo}" style="max-width:38px; max-height:38px; object-fit:contain; margin:0 auto; display:block;"/></div>',
                unsafe_allow_html=True
            )
        elif os.path.exists("assets/logo.jpg"):
            st.image("assets/logo.jpg", width=38)
        else:
            st.markdown("**EPP**")
    else:
        if sidebar_logo:
            st.markdown(
                f'<img src="{sidebar_logo}" style="width:100%; max-height:120px; object-fit:contain; display:block; margin:0 auto;"/>',
                unsafe_allow_html=True
            )
        elif os.path.exists("assets/logo.jpg"):
            st.image("assets/logo.jpg", use_container_width=True)
        else:
            st.markdown("### VIGILANTE EPP")
        st.caption("**Sistema Inteligente de Seguridad 4.0**")

    st.divider()
    if not st.session_state.sidebar_mini:
        st.markdown("#### Navegacion")

    nav_items = [
        ("demo", "Demostracion", "Demostracion"),
        ("live", "Analisis en Vivo", "Analisis en Vivo"),
        ("stats", "Estadisticas", "Estadisticas"),
        ("reports", "Reportes", "Reportes"),
    ]

    def _navigate_to(target_page):
        st.session_state.current_page = target_page

    for nav_id, nav_label, nav_val in nav_items:
        st.markdown(f'<div class="nav-anchor" data-nav="{nav_id}"></div>', unsafe_allow_html=True)
        is_active = (st.session_state.current_page == nav_val)
        btn_type = "primary" if is_active else "secondary"
        st.button(
            nav_label,
            key=f"nav_btn_{nav_id}",
            type=btn_type,
            use_container_width=True,
            on_click=_navigate_to,
            args=(nav_val,),
            help=nav_label
        )

    st.divider()

    st.markdown('<div class="nav-anchor" data-nav="settings"></div>', unsafe_allow_html=True)
    if st.button(
        "Configuracion",
        key="nav_btn_settings",
        use_container_width=True,
        help="Configuracion del Sistema"
    ):
        st.session_state["dlg_is_dark"] = st.session_state.config["is_dark"]
        st.session_state["dlg_helmet"] = st.session_state.config["check_helmet"]
        st.session_state["dlg_vest"] = st.session_state.config["check_vest"]
        st.session_state["dlg_sensitivity"] = st.session_state.config["sensitivity_mode"]
        config_dialog(model_info)

    st.markdown('<div class="nav-anchor" data-nav="toggle"></div>', unsafe_allow_html=True)
    toggle_label = "Contraer" if not st.session_state.sidebar_mini else "Expandir"
    toggle_help = "Colapsar a modo riel" if not st.session_state.sidebar_mini else "Expandir barra de navegacion"
    if st.button(
        toggle_label,
        key="nav_btn_toggle",
        use_container_width=True,
        help=toggle_help
    ):
        st.session_state.sidebar_mini = not st.session_state.sidebar_mini
        st.rerun()

cfg = st.session_state.config
is_dark = cfg["is_dark"]
st.session_state["is_dark"] = is_dark
st.session_state["conf_threshold_pct"] = cfg["conf_threshold_pct"]
st.session_state["check_helmet"] = cfg["check_helmet"]
st.session_state["check_vest"] = cfg["check_vest"]
st.session_state["sensitivity_mode"] = cfg["sensitivity_mode"]

apply_styles(is_dark, is_mini=st.session_state.sidebar_mini)
st.markdown(render_top_header(is_dark), unsafe_allow_html=True)

page = st.session_state.current_page
demo_video = get_demo_video_service()
if (
    page != "Demostracion"
    and st.session_state.get("demo_video_run_id") == demo_video.get_run_id()
    and getattr(demo_video, "is_busy", lambda: demo_video.is_running())()
):
    demo_video.stop()

if "Demostracion" in page:
    render_demo_view(model, is_dark, cfg)
elif "Analisis en Vivo" in page:
    render_live_view(model, is_dark, cfg)
elif "Estadisticas" in page:
    render_stats_view(is_dark)
elif "Reportes" in page:
    render_reports_view(is_dark)
