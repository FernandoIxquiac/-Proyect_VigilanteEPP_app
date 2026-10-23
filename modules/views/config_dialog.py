"""Dialogo modal emergente para configuracion global del sistema."""

import streamlit as st
from modules.auditor import get_live_auditor
from modules.demo_video import get_demo_video_service
from modules.camera import get_camera_manager
from modules.metrics import reset_session_state

SENSITIVITY_MAP = {
    "Minima": 65,
    "Media": 45,
    "Alta": 30,
    "Maxima": 20,
}


@st.dialog("Configuracion del Sistema", width="medium")
def config_dialog(model_info: str = "YOLOv8 (Activo)"):
    """Dialogo modal emergente para ajustar parametros globales del sistema."""
    cfg = st.session_state.config

    if "dlg_is_dark" not in st.session_state:
        st.session_state["dlg_is_dark"] = cfg["is_dark"]
    if "dlg_helmet" not in st.session_state:
        st.session_state["dlg_helmet"] = cfg["check_helmet"]
    if "dlg_vest" not in st.session_state:
        st.session_state["dlg_vest"] = cfg["check_vest"]
    if "dlg_sensitivity" not in st.session_state:
        st.session_state["dlg_sensitivity"] = cfg.get("sensitivity_mode", "Media")

    def _sync_dark():
        new_val = st.session_state.dlg_is_dark
        st.session_state.config["is_dark"] = new_val
        st.session_state["is_dark"] = new_val
        get_live_auditor().set_theme(new_val)

    def _sync_helmet():
        new_val = st.session_state.dlg_helmet
        st.session_state.config["check_helmet"] = new_val
        st.session_state["check_helmet"] = new_val

    def _sync_vest():
        new_val = st.session_state.dlg_vest
        st.session_state.config["check_vest"] = new_val
        st.session_state["check_vest"] = new_val

    def _sync_sensitivity():
        selected = st.session_state.dlg_sensitivity
        st.session_state.config["sensitivity_mode"] = selected
        st.session_state["sensitivity_mode"] = selected
        conf_val = SENSITIVITY_MAP.get(selected, 45)
        st.session_state.config["conf_threshold_pct"] = conf_val
        st.session_state["conf_threshold_pct"] = conf_val

    col_theme, col_filters = st.columns(2)
    with col_theme:
        st.markdown('<div class="section-header">Tema Visual</div>', unsafe_allow_html=True)
        st.toggle(
            "Modo Oscuro",
            key="dlg_is_dark",
            on_change=_sync_dark,
            help="Activa o desactiva el tema oscuro de la interfaz instantaneamente."
        )
    with col_filters:
        st.markdown('<div class="section-header">Filtros EPP</div>', unsafe_allow_html=True)
        st.checkbox(
            "Casco de Seguridad",
            key="dlg_helmet",
            on_change=_sync_helmet,
            help="Activa la verificacion obligatoria de uso de casco reglamentario."
        )
        st.checkbox(
            "Chaleco Reflectante",
            key="dlg_vest",
            on_change=_sync_vest,
            help="Activa la verificacion obligatoria de uso de chaleco reflectante."
        )

    st.markdown(
        '<div class="section-header" style="margin-top:14px; margin-bottom:22px;">Sensibilidad del Modelo</div>',
        unsafe_allow_html=True
    )
    sens_options = ["Minima", "Media", "Alta", "Maxima"]
    current_mode = cfg.get("sensitivity_mode", "Media")
    if current_mode not in sens_options:
        current_mode = "Media"

    st.select_slider(
        "Nivel de sensibilidad:",
        options=sens_options,
        key="dlg_sensitivity",
        on_change=_sync_sensitivity,
        label_visibility="collapsed",
        help="Minima (65%): Deteccion estricta. Media (45%): Balance estandar. Alta (30%): Detecta operarios lejanos. Maxima (20%): Maxima captura."
    )

    explanations = {
        "Minima": "Umbral 65% - Deteccion estricta, minima tasa de falsas alarmas.",
        "Media": "Umbral 45% - Balance recomendado para planta operativa.",
        "Alta": "Umbral 30% - Sensibilidad alta, detecta operarios lejanos o parciales.",
        "Maxima": "Umbral 20% - Maxima captura para auditorias exhaustivas."
    }
    st.caption(explanations.get(current_mode, ""))

    col_engine, col_session = st.columns(2)
    with col_engine:
        st.markdown('<div class="section-header">Motor IA</div>', unsafe_allow_html=True)
        st.info(f"**Modelo activo:** {model_info}")
    with col_session:
        st.markdown('<div class="section-header">Sesion Activa</div>', unsafe_allow_html=True)
        st.caption(f"Turno Activo: Sesion #{st.session_state.get('current_session_id', 1)}")
        if st.button(
            "Iniciar Nuevo Turno",
            use_container_width=True,
            help="Cierra el turno actual y abre uno nuevo sin borrar registros anteriores."
        ):
            reset_session_state()
            st.rerun()

    st.markdown('<div class="section-header" style="margin-top:12px;">Mantenimiento y Cache</div>', unsafe_allow_html=True)
    if st.button(
        "Reiniciar Cache y Servicios",
        use_container_width=True,
        help="Libera la memoria interna de Streamlit, recarga los modulos y reinicia los servicios de vision."
    ):
        get_camera_manager().stop_all()
        get_live_auditor().stop()
        get_demo_video_service().stop()
        st.cache_resource.clear()
        st.cache_data.clear()
        st.rerun()

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Listo", type="primary", use_container_width=True):
            st.rerun()
    with col_b:
        if st.button("Cerrar", use_container_width=True):
            st.rerun()
