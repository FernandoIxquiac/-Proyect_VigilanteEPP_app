"""Vista de analisis y supervision en vivo de planta (Live Auditor)."""

import time
import streamlit as st

from styles import render_status_card, render_incident_card
from modules.auditor import get_live_auditor
from modules.demo_video import get_demo_video_service
from modules.camera_sources import CAMERA_MODE_LOCK, get_camera_options, resolve_camera_source
from modules.database import get_or_create_active_session, get_compliance_stats, get_recent_incidents
from modules.views.components import render_stream_presets, render_device_scanner, render_desktop_window_card


def render_live_view(model, is_dark: bool, cfg: dict):
    """Renderiza el panel de control de camara en vivo y telemetria pericial."""
    auditor = get_live_auditor()
    demo_video = get_demo_video_service()
    is_auditing = auditor.is_running()
    conf_threshold = cfg["conf_threshold_pct"] / 100.0
    check_helmet = cfg["check_helmet"]
    check_vest = cfg["check_vest"]
    start_requested = False
    stop_requested = False

    col_pwr, col_src = st.columns([1.1, 2.9])

    with col_pwr:
        st.markdown('<div class="section-header">Control de Camara</div>', unsafe_allow_html=True)

        camera_toggle = st.toggle(
            "Camara Activa",
            value=is_auditing,
            key="camera_power_toggle",
            help="Activa o detiene la captura de video y la auditoria en tiempo real.",
        )

        if camera_toggle and not is_auditing:
            start_requested = True
        elif not camera_toggle and is_auditing:
            stop_requested = True

        if is_auditing:
            st.markdown('<div class="status-indicator-running">● CAMARA EN VIVO</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-indicator-stopped">○ CAMARA DETENIDA</div>', unsafe_allow_html=True)

    with col_src:
        st.markdown('<div class="section-header">Dispositivo de Video</div>', unsafe_allow_html=True)
        camera_options = get_camera_options(st.session_state.get("_detected_cameras"))
        saved_camera_choice = st.session_state.get("camera_source_choice", camera_options[0])
        camera_index = camera_options.index(saved_camera_choice) if saved_camera_choice in camera_options else 0
        camera_source_choice = st.selectbox(
            "Dispositivo:",
            camera_options,
            index=camera_index,
            disabled=is_auditing,
            label_visibility="collapsed",
            help="Selecciona qué cámara capturará el video."
        )
        st.session_state.camera_source_choice = camera_source_choice

        custom_stream_url = ""
        if "RTSP / IP" in camera_source_choice:
            render_stream_presets("live", "camera_stream_url")
            custom_stream_url = st.text_input(
                "URL del Flujo RTSP / HTTP:",
                value=st.session_state.get("camera_stream_url", "http://192.168.1.50:8080/video"),
                help="Ingresa la URL del flujo de video"
            )
            st.session_state.camera_stream_url = custom_stream_url
            st.caption("Aviso técnico: Para Galaxy A21 o Tab en Wi-Fi, mantenga el dispositivo en la misma red local y con pantalla en brillo mínimo.")
        elif "Cam-" in camera_source_choice and not is_auditing:
            render_device_scanner("live_btn_scan_devices")

        cam_source, cam_desc = resolve_camera_source(camera_source_choice, custom_stream_url)

    if stop_requested:
        auditor.stop()
        st.rerun()

    if start_requested:
        if isinstance(cam_source, str) and not cam_source:
            st.error("Ingresa una dirección RTSP o HTTP antes de iniciar la cámara.")
        else:
            with CAMERA_MODE_LOCK:
                demo_busy_now = getattr(demo_video, "is_busy", lambda: demo_video.is_running())()
                live_started = False if demo_busy_now else auditor.start(
                    source=cam_source,
                    source_desc=cam_desc,
                    model=model,
                    conf_threshold=conf_threshold,
                    check_helmet=check_helmet,
                    check_vest=check_vest,
                    show_native_window=True,
                )
            if demo_busy_now:
                st.error("La demostración está liberando la cámara. Espera un momento y vuelve a iniciar.")
            elif live_started:
                st.session_state.current_session_id = get_or_create_active_session()
                st.rerun()
            else:
                st.error("La cámara anterior aún está cerrándose. Espera un momento y vuelve a iniciar.")

    if is_auditing:
        auditor.set_native_window(True)
        auditor.update_config(
            conf_threshold=conf_threshold,
            check_helmet=check_helmet,
            check_vest=check_vest
        )

    st.markdown('<div class="layout-spacer"></div>', unsafe_allow_html=True)

    def _get_live_db_snapshot(state):
        active_sid = state.get("session_id") or st.session_state.get("current_session_id")
        now_ts = time.monotonic()
        cache_key = (
            active_sid,
            state.get("session_events", 0),
            state.get("session_infractions", 0),
        )
        if (
            st.session_state.get("_live_db_cache_key") != cache_key
            or now_ts - st.session_state.get("_last_live_db_query_monotonic", 0.0) > 1.5
            or "_live_cached_stats" not in st.session_state
            or "_live_cached_recent" not in st.session_state
        ):
            st.session_state["_live_cached_stats"] = get_compliance_stats(session_id=active_sid)
            st.session_state["_live_cached_recent"] = get_recent_incidents(session_id=active_sid, limit=4)
            st.session_state["_live_db_cache_key"] = cache_key
            st.session_state["_last_live_db_query_monotonic"] = now_ts
        return st.session_state["_live_cached_stats"], st.session_state["_live_cached_recent"]

    col_cam, col_recent = st.columns([0.70, 0.30])
    with col_cam:
        native_state = auditor.get_latest_state()
        if auditor.is_running():
            render_desktop_window_card(
                "◈ VENTANA DE ESCRITORIO ACTIVA",
                "El video y las detecciones se muestran en una ventana independiente. Puedes moverla al segundo monitor y seguir usando este panel para consultar las estadísticas."
            )
        elif native_state.get("status") == "danger":
            st.error(native_state.get("message") or "No se pudo abrir la cámara seleccionada.")
        else:
            st.info("Presiona 'Iniciar Cámara' para abrir la ventana de video en este equipo.")

    with col_recent:
        @st.fragment(run_every="1s")
        def _live_recent_render():
            state = auditor.get_latest_state()
            _, recent_events = _get_live_db_snapshot(state)
            st.markdown('<div class="feed-header">ÚLTIMAS AUDITORÍAS (TURNO)</div>', unsafe_allow_html=True)
            if recent_events:
                inc_cards = "".join(
                    render_incident_card(inc["time"], inc["title"], inc["badge"], is_dark)
                    for inc in recent_events
                )
                st.markdown(f"<div>{inc_cards}</div>", unsafe_allow_html=True)
            else:
                st.caption("Esperando eventos en este turno...")

        _live_recent_render()

    @st.fragment(run_every="1s")
    def _live_metrics_render():
        state = auditor.get_latest_state()
        stats, _ = _get_live_db_snapshot(state)
        t_insp, p_pct, _, p_infr = stats
        persistence_error = state.get("persistence_last_error")
        if persistence_error:
            st.warning(f"Persistencia de auditoría: {persistence_error}")
        st.caption(
            "Eventos guardados: "
            f"{state.get('persistence_persisted_events', 0)}; pendientes: "
            f"{state.get('persistence_pending_events', 0)}; rechazados: "
            f"{state.get('persistence_rejected_events', 0)}; fallidos: "
            f"{state.get('persistence_failed_events', 0)}"
        )
        st.markdown('<div class="layout-spacer"></div>', unsafe_allow_html=True)
        col_status_card, col_kpi1, col_kpi2, col_kpi3 = st.columns([0.43, 0.19, 0.19, 0.19])
        with col_status_card:
            st.markdown(
                render_status_card(
                    state.get("status", "standby"),
                    state.get("title", "SISTEMA EN ESPERA"),
                    state.get("message", "Inicia la transmisión para comenzar la auditoría."),
                    is_dark=is_dark,
                    personnel_count=state.get("persons_count", 0)
                ),
                unsafe_allow_html=True
            )
        with col_kpi1:
            st.metric(label="Auditorías", value=f"{t_insp}")
        with col_kpi2:
            compliance_value = "—" if state.get("status") == "initializing" else f"{p_pct}%"
            st.metric(label="Cumplimiento", value=compliance_value)
        with col_kpi3:
            st.metric(label="Infracciones", value=f"{p_infr}")

    _live_metrics_render()
