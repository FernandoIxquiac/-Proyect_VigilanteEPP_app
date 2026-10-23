"""Componentes visuales y controles reutilizables para la interfaz Streamlit."""

import streamlit as st
from modules.camera_sources import STREAM_PRESETS, scan_available_cameras


def render_stream_presets(prefix: str, url_state_key: str):
    """Renderiza botones de plantillas rapidas para flujos IP/RTSP."""
    st.markdown(
        '<div class="preset-hint">Plantillas de conexión rápida:</div>',
        unsafe_allow_html=True
    )
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("● IP Webcam (:8080)", key=f"{prefix}_btn_ipwebcam", use_container_width=True, help="Aplica plantilla para app IP Webcam"):
            st.session_state[url_state_key] = STREAM_PRESETS["IP Webcam (Android :8080)"]
            st.rerun()
    with col2:
        if st.button("● DroidCam (:4747)", key=f"{prefix}_btn_droidcam", use_container_width=True, help="Aplica plantilla para app DroidCam"):
            st.session_state[url_state_key] = STREAM_PRESETS["DroidCam (Android/iOS :4747)"]
            st.rerun()
    with col3:
        if st.button("● RTSP (:554)", key=f"{prefix}_btn_rtsp", use_container_width=True, help="Aplica plantilla RTSP de seguridad"):
            st.session_state[url_state_key] = STREAM_PRESETS["RTSP Seguridad (:554)"]
            st.rerun()


def render_device_scanner(btn_key: str):
    """Renderiza el boton de escaneo de camaras USB/UVC y actualiza el estado."""
    if st.button("≡ Escanear Puertos USB / UVC", key=btn_key, help="Detecta nuevos dispositivos USB (Galaxy S24 FE / Tab / Webcams)"):
        detected = scan_available_cameras(max_indices=5, force_refresh=True)
        st.session_state["_detected_cameras"] = detected
        st.rerun()


def render_desktop_window_card(title: str, description: str):
    """Renderiza tarjeta informativa de ventana nativa de escritorio."""
    st.markdown(
        f"""
        <div class="hud-card">
            <div class="hud-card-title">{title}</div>
            <div class="hud-card-desc">{description}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
