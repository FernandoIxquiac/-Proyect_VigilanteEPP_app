"""Vista de demostracion y pruebas sinteticas/multimedia (Sandbox)."""

import cv2
import numpy as np
from PIL import Image
import streamlit as st

from styles import render_status_card, render_incident_card
from modules.demo_video import get_demo_video_service
from modules.auditor import get_live_auditor
from modules.camera_sources import CAMERA_MODE_LOCK, get_camera_options, resolve_camera_source
from modules.samples import generate_demo_sample
from modules.views.components import render_stream_presets, render_device_scanner, render_desktop_window_card


def render_demo_view(model, is_dark: bool, cfg: dict):
    """Renderiza el panel de demostracion interactiva y sandbox visual."""
    demo_video = get_demo_video_service()
    conf_threshold = cfg["conf_threshold_pct"] / 100.0
    check_helmet = cfg["check_helmet"]
    check_vest = cfg["check_vest"]

    if demo_video.is_running():
        demo_video.update_config(conf_threshold, check_helmet, check_vest)

    is_demo_running = demo_video.is_running()
    demo_busy = getattr(demo_video, "is_busy", lambda: demo_video.is_running())()
    start_demo_requested = False
    stop_demo_requested = False

    dynamic_demo_cameras = get_camera_options(st.session_state.get("_detected_cameras"))
    demo_source_options = (
        *dynamic_demo_cameras[:-1],
        "Flujo RTSP / IP",
        "Archivo de Imagen (Subir Foto)",
        "Escenas Sinteticas de Prueba",
    )

    col_pwr, col_src = st.columns([1.1, 2.9])

    with col_pwr:
        st.markdown('<div class="section-header">Control de Demostración</div>', unsafe_allow_html=True)

        demo_toggle = st.toggle(
            "Demostracion Activa",
            value=is_demo_running,
            key="demo_power_toggle",
            help="Activa o detiene la demostracion en la ventana flotante de escritorio.",
        )

        if demo_toggle and not is_demo_running:
            start_demo_requested = True
        elif not demo_toggle and is_demo_running:
            stop_demo_requested = True

        if is_demo_running:
            st.markdown('<div class="status-indicator-running">● DEMO EN VIVO</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-indicator-stopped">○ DEMO DETENIDA</div>', unsafe_allow_html=True)

    with col_src:
        st.markdown('<div class="section-header">Fuente de Demostración</div>', unsafe_allow_html=True)
        saved_demo_choice = st.session_state.get("demo_camera_choice", demo_source_options[0])
        demo_index = demo_source_options.index(saved_demo_choice) if saved_demo_choice in demo_source_options else 0
        demo_choice = st.selectbox(
            "Fuente de demostración:",
            demo_source_options,
            index=demo_index,
            key="demo_camera_selector",
            disabled=is_demo_running,
            label_visibility="collapsed",
            help="Selecciona el origen para la prueba de demostración."
        )
        st.session_state.demo_camera_choice = demo_choice

        demo_stream_url = ""
        uploaded_demo_file = None
        synthetic_demo_choice = None

        if demo_choice == "Flujo RTSP / IP":
            render_stream_presets("demo", "demo_camera_stream_url")
            demo_stream_url = st.text_input(
                "URL del Flujo RTSP / HTTP para Demostración:",
                value=st.session_state.get("demo_camera_stream_url", "http://192.168.1.50:8080/video"),
                disabled=is_demo_running,
                key="demo_camera_stream_url",
                help="Ingresa la URL del flujo de video para demostración."
            )
            st.session_state.demo_camera_stream_url = demo_stream_url
            st.caption("Aviso técnico: Para Galaxy A21 o Tab en Wi-Fi, mantenga el dispositivo en la misma red local y con pantalla en brillo mínimo.")

        elif "Cam-" in demo_choice and not is_demo_running:
            render_device_scanner("demo_btn_scan_devices")

        elif demo_choice == "Archivo de Imagen (Subir Foto)":
            uploaded_demo_file = st.file_uploader(
                "Subir fotografía de inspección (.jpg, .png)",
                type=["jpg", "jpeg", "png"],
                disabled=is_demo_running,
                key="demo_file_uploader"
            )
            if uploaded_demo_file is not None:
                file_sig = f"{uploaded_demo_file.name}_{uploaded_demo_file.size}"
                if st.session_state.get("_last_demo_file_sig") != file_sig:
                    pil_img = Image.open(uploaded_demo_file)
                    bgr_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
                    demo_video.display_static_image(
                        bgr_img,
                        model,
                        conf_threshold,
                        check_helmet=check_helmet,
                        check_vest=check_vest,
                        sample_name=uploaded_demo_file.name
                    )
                    st.session_state["_last_demo_file_sig"] = file_sig

        elif demo_choice == "Escenas Sinteticas de Prueba":
            synthetic_scenarios = [
                "Caso 1042: Obrero con EPP Completo",
                "Caso 1043: Infraccion Falta de Casco"
            ]
            saved_synth = st.session_state.get("demo_synth_choice", synthetic_scenarios[0])
            synth_idx = synthetic_scenarios.index(saved_synth) if saved_synth in synthetic_scenarios else 0
            synthetic_demo_choice = st.selectbox(
                "Seleccionar escenario sintético:",
                synthetic_scenarios,
                index=synth_idx,
                disabled=is_demo_running,
                key="demo_sample_selector"
            )
            st.session_state.demo_synth_choice = synthetic_demo_choice
            synth_sig = f"synth_{synthetic_demo_choice}"
            if st.session_state.get("_last_demo_synth_sig") != synth_sig:
                synth_pil = generate_demo_sample(synthetic_demo_choice)
                synth_bgr = cv2.cvtColor(np.array(synth_pil), cv2.COLOR_RGB2BGR)
                demo_video.display_static_image(
                    synth_bgr,
                    model,
                    conf_threshold,
                    check_helmet=check_helmet,
                    check_vest=check_vest,
                    sample_name=synthetic_demo_choice
                )
                st.session_state["_last_demo_synth_sig"] = synth_sig

    if stop_demo_requested:
        demo_video.stop()
        st.session_state["_last_demo_file_sig"] = None
        st.session_state["_last_demo_synth_sig"] = None
        st.rerun()

    if start_demo_requested:
        if demo_choice == "Archivo de Imagen (Subir Foto)":
            if uploaded_demo_file is not None:
                pil_img = Image.open(uploaded_demo_file)
                bgr_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
                demo_video.display_static_image(
                    bgr_img,
                    model,
                    conf_threshold,
                    check_helmet=check_helmet,
                    check_vest=check_vest,
                    sample_name=uploaded_demo_file.name
                )
                st.rerun()
            else:
                st.info("Sube una imagen para proyectarla en la ventana de escritorio.")
        elif demo_choice == "Escenas Sinteticas de Prueba":
            if synthetic_demo_choice:
                synth_pil = generate_demo_sample(synthetic_demo_choice)
                synth_bgr = cv2.cvtColor(np.array(synth_pil), cv2.COLOR_RGB2BGR)
                demo_video.display_static_image(
                    synth_bgr,
                    model,
                    conf_threshold,
                    check_helmet=check_helmet,
                    check_vest=check_vest,
                    sample_name=synthetic_demo_choice
                )
                st.rerun()
        else:
            if demo_busy:
                st.warning("La cámara anterior aún está cerrándose. Espera un momento y vuelve a iniciar.")
            else:
                demo_source, _ = resolve_camera_source(demo_choice, demo_stream_url)
                if isinstance(demo_source, str) and not demo_source:
                    st.error("Ingresa una dirección RTSP o HTTP válida.")
                else:
                    with CAMERA_MODE_LOCK:
                        live_busy = getattr(get_live_auditor(), "is_busy", lambda: get_live_auditor().is_running())()
                        demo_started = False if live_busy else demo_video.start(
                            source=demo_source,
                            model=model,
                            conf_threshold=conf_threshold,
                            check_helmet=check_helmet,
                            check_vest=check_vest,
                        )
                    if live_busy:
                        st.error("Detén el análisis en vivo antes de iniciar la demostración con cámara.")
                    elif demo_started:
                        st.session_state.demo_video_run_id = demo_video.get_run_id()
                        st.rerun()
                    else:
                        st.error(demo_video.get_state().get("message", "No se pudo iniciar la demostración."))

    st.markdown('<div class="layout-spacer"></div>', unsafe_allow_html=True)

    col_cam, col_recent = st.columns([0.70, 0.30])
    with col_cam:
        demo_state = demo_video.get_state()
        if demo_state.get("status") == "danger" and not is_demo_running:
            st.error(demo_state.get("message") or "Error en la demostración.")
        render_desktop_window_card(
            "◈ VENTANA DE ESCRITORIO ACTIVA (DEMOSTRACION)",
            "El video o imagen analizada se proyecta en la ventana flotante de escritorio. Este modo no almacena eventos en la base de datos ni evidencias en disco."
        )

    with col_recent:
        @st.fragment(run_every="1s")
        def _demo_recent_render():
            state = demo_video.get_state()
            recent_events = state.get("recent_events", [])
            st.markdown('<div class="feed-header">ÚLTIMAS AUDITORÍAS (DEMOSTRACIÓN)</div>', unsafe_allow_html=True)
            if recent_events:
                inc_cards = "".join(
                    render_incident_card(inc["time"], inc["title"], inc["badge"], is_dark)
                    for inc in recent_events
                )
                st.markdown(f"<div>{inc_cards}</div>", unsafe_allow_html=True)
            else:
                st.caption("Esperando eventos de demostración...")

        _demo_recent_render()

    @st.fragment(run_every="1s")
    def _demo_metrics_render():
        state = demo_video.get_state()
        st.markdown('<div class="layout-spacer"></div>', unsafe_allow_html=True)
        col_status_card, col_kpi1, col_kpi2, col_kpi3 = st.columns([0.43, 0.19, 0.19, 0.19])
        with col_status_card:
            st.markdown(
                render_status_card(
                    state.get("status", "standby"),
                    state.get("title", "SISTEMA EN ESPERA"),
                    state.get("message", "Inicia la demostración para comenzar el análisis."),
                    is_dark=is_dark,
                    personnel_count=state.get("persons_count", 0)
                ),
                unsafe_allow_html=True
            )
        with col_kpi1:
            st.metric(label="Auditorias (Demo)", value=f"{state.get('total_inspections', 0)}")
        with col_kpi2:
            compliance_value = "—" if state.get("status") == "initializing" else f"{state.get('compliance_pct', 100.0)}%"
            st.metric(label="Cumplimiento", value=compliance_value)
        with col_kpi3:
            st.metric(label="Infracciones", value=f"{state.get('infractions_count', 0)}")

    _demo_metrics_render()
