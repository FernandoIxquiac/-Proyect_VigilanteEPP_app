import os
import time
import datetime
import cv2
import numpy as np
from PIL import Image
import streamlit as st
import pandas as pd

# Módulos personalizados (Arquitectura modular)
from styles import (
    apply_styles,
    render_top_header,
    render_status_card,
    render_incident_card,
    _get_logo_base64
)
from modules.detector import (
    load_detector_model,
    detect_objects,
    evaluate_compliance,
    analyze_workers_spatial
)
from modules.metrics import (
    init_session_state,
    reset_session_state,
    record_camera_audit,
    get_compliance_stats,
    get_recent_incidents,
    calculate_roi,
    get_history_dataframe,
    get_detailed_events_dataframe,
    get_hourly_risk_distribution
)
from modules.database import (
    start_camera_session,
    end_camera_session,
    get_all_sessions_list
)
from modules.tracker_manager import WorkerTrackManager
from modules.report_generator import (
    compute_audit_kpis,
    generate_html_report
)
from modules.samples import generate_demo_sample
from modules.camera import get_camera_manager
from modules.charts import (
    create_spc_control_chart,
    create_severity_bar_chart
)


# ----------------- 1. CONFIGURACIÓN INICIAL DE STREAMLIT -----------------
st.set_page_config(
    page_title="VIGILANTE EPP - Detector Inteligente",
    page_icon="assets/logo.jpg",
    layout="wide",
    initial_sidebar_state="expanded"
)

init_session_state()

# Mapeo de sensibilidad industrial
_SENSITIVITY_MAP = {
    "Minima": 65,
    "Media": 45,
    "Alta": 30,
    "Maxima": 20
}
_INV_SENSITIVITY_MAP = {v: k for k, v in _SENSITIVITY_MAP.items()}

# Estructura maestra persistente de configuración del sistema
if "config" not in st.session_state:
    st.session_state.config = {
        "is_dark": True,
        "check_helmet": True,
        "check_vest": True,
        "sensitivity_mode": "Media",
        "conf_threshold_pct": 45
    }

# Sincronización inicial con claves compatibles en st.session_state
for _k, _v in st.session_state.config.items():
    st.session_state.setdefault(_k, _v)

# ----------------- 2. CARGA DE MODELO -----------------
model, model_info = load_detector_model()


# ----------------- 3. MODAL DE CONFIGURACIÓN -----------------
@st.dialog("Configuracion del Sistema", width="small")
def config_dialog():
    """Dialogo modal emergente para ajustar parametros globales del sistema."""
    cfg = st.session_state.config

    def _sync_dark():
        new_val = st.session_state.dlg_is_dark
        st.session_state.config["is_dark"] = new_val
        st.session_state["is_dark"] = new_val
        st.rerun()

    def _sync_helmet():
        new_val = st.session_state.dlg_helmet
        st.session_state.config["check_helmet"] = new_val
        st.session_state["check_helmet"] = new_val
        st.rerun()

    def _sync_vest():
        new_val = st.session_state.dlg_vest
        st.session_state.config["check_vest"] = new_val
        st.session_state["check_vest"] = new_val
        st.rerun()

    def _sync_sensitivity():
        selected = st.session_state.dlg_sensitivity
        st.session_state.config["sensitivity_mode"] = selected
        st.session_state["sensitivity_mode"] = selected
        conf_val = _SENSITIVITY_MAP.get(selected, 45)
        st.session_state.config["conf_threshold_pct"] = conf_val
        st.session_state["conf_threshold_pct"] = conf_val
        st.rerun()

    st.markdown("#### Tema Visual")
    st.toggle(
        "Modo Oscuro",
        value=cfg["is_dark"],
        key="dlg_is_dark",
        on_change=_sync_dark,
        help="Activa o desactiva el tema oscuro de la interfaz instantaneamente."
    )
    st.divider()

    st.markdown("#### Parametros de Deteccion")
    st.checkbox(
        "Casco de Seguridad",
        value=cfg["check_helmet"],
        key="dlg_helmet",
        on_change=_sync_helmet,
        help="Activa la verificacion obligatoria de uso de casco reglamentario."
    )
    st.checkbox(
        "Chaleco Reflectante",
        value=cfg["check_vest"],
        key="dlg_vest",
        on_change=_sync_vest,
        help="Activa la verificacion obligatoria de uso de chaleco reflectante."
    )
    st.divider()

    st.markdown("#### Sensibilidad del Modelo")
    sens_options = ["Minima", "Media", "Alta", "Maxima"]
    current_mode = cfg.get("sensitivity_mode", "Media")
    if current_mode not in sens_options:
        current_mode = "Media"

    st.select_slider(
        "Nivel de sensibilidad:",
        options=sens_options,
        value=current_mode,
        key="dlg_sensitivity",
        on_change=_sync_sensitivity,
        help="Minima (65%): Deteccion estricta, minima tasa de falsas alarmas. Media (45%): Balance estandar para planta. Alta (30%): Detecta operarios lejanos. Maxima (20%): Maxima captura para auditorias exhaustivas."
    )

    _explanations = {
        "Minima": "Umbral 65% - Deteccion estricta, minima tasa de falsas alarmas.",
        "Media": "Umbral 45% - Balance recomendado para planta operativa.",
        "Alta": "Umbral 30% - Sensibilidad alta, detecta operarios lejanos o parciales.",
        "Maxima": "Umbral 20% - Maxima captura para auditorias exhaustivas."
    }
    st.caption(_explanations.get(current_mode, ""))
    st.divider()

    st.markdown("#### Motor IA")
    st.info(f"**Modelo activo:** {model_info}")
    st.divider()

    st.markdown("#### Sesion Activa")
    st.caption(f"Turno Activo: Sesion #{st.session_state.get('current_session_id', 1)}")
    if st.button(
        "Iniciar Nuevo Turno / Sesion",
        use_container_width=True,
        help="Cierra el turno actual y abre uno nuevo sin borrar registros anteriores."
    ):
        reset_session_state()
        st.rerun()
    st.divider()

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Listo", type="primary", use_container_width=True):
            st.rerun()
    with col_b:
        if st.button("Cerrar", use_container_width=True):
            st.rerun()


# ----------------- 4. SIDEBAR DE NAVEGACIÓN -----------------
with st.sidebar:
    # Mostrar logo SVG en Base64 para nitidez vectorial; fallback a JPG
    _sidebar_logo = _get_logo_base64()
    if _sidebar_logo:
        st.markdown(
            f'<img src="{_sidebar_logo}" style="width:100%; max-height:140px; object-fit:contain; display:block; margin:0 auto;"/>',
            unsafe_allow_html=True
        )
    elif os.path.exists("assets/logo.jpg"):
        st.image("assets/logo.jpg", use_container_width=True)
    else:
        st.markdown("### VIGILANTE EPP")
    st.caption("**Sistema Inteligente de Seguridad 4.0**")

    st.divider()
    st.markdown("#### Navegación")
    page = st.radio(
        label="",
        options=["◈ Demostracion", "◉ Analisis en Vivo", "▲ Estadisticas", "≡ Reportes"],
        label_visibility="collapsed"
    )

    st.divider()
    if st.button("⚙ Configuracion", use_container_width=True):
        st.session_state["dlg_is_dark"] = st.session_state.config["is_dark"]
        st.session_state["dlg_helmet"] = st.session_state.config["check_helmet"]
        st.session_state["dlg_vest"] = st.session_state.config["check_vest"]
        st.session_state["dlg_sensitivity"] = st.session_state.config["sensitivity_mode"]
        config_dialog()

# Lectura de parámetros desde st.session_state.config
cfg = st.session_state.config
is_dark = cfg["is_dark"]
conf_threshold = cfg["conf_threshold_pct"] / 100.0
check_helmet = cfg["check_helmet"]
check_vest = cfg["check_vest"]

# Sincronización hacia claves compatibles en st.session_state
st.session_state["is_dark"] = is_dark
st.session_state["conf_threshold_pct"] = cfg["conf_threshold_pct"]
st.session_state["check_helmet"] = check_helmet
st.session_state["check_vest"] = check_vest
st.session_state["sensitivity_mode"] = cfg["sensitivity_mode"]

# Aplicar estilos CSS globales según el tema activo
apply_styles(is_dark)

# Renderizar barra superior HUD
st.markdown(render_top_header(is_dark), unsafe_allow_html=True)


# =========================================================
# SECCIÓN 1: DEMOSTRACIÓN (SANDBOX)
# =========================================================
if "Demostracion" in page:
    st.warning("**MODO DEMOSTRACIÓN — Sin almacenamiento de datos**\n\nPrueba el sistema de detección sin guardar registros. Sube tu propia imagen o usa una escena sintética.")

    col_upload, col_synthetic = st.columns([1.5, 1])

    with col_upload:
        uploaded_file = st.file_uploader(
            "Subir fotografía de inspección (.jpg, .png)",
            type=["jpg", "jpeg", "png"]
        )

    with col_synthetic:
        demo_sample = st.selectbox(
            "Opciones de escena sintética:",
            ["Sin selección", "Caso 1042: Obrero con EPP Completo", "Caso 1043: Infraccion Falta de Casco"]
        )
        generate_btn = st.button("Generar Escena Sintética", use_container_width=True)

    img_input = None
    sample_name = ""

    if uploaded_file is not None:
        img_input = Image.open(uploaded_file)
        sample_name = uploaded_file.name
    elif demo_sample != "Sin selección":
        img_input = generate_demo_sample(demo_sample)
        sample_name = demo_sample

    if img_input is not None:
        st.markdown("---")
        st.markdown("#### Comparador Visual Lado a Lado")
        col_orig, col_analyzed = st.columns(2)

        with col_orig:
            st.markdown("**1. Imagen de Entrada (Original)**")
            st.image(img_input, use_container_width=True)

        with col_analyzed:
            st.markdown("**2. Análisis de Detección**")
            img_cv = cv2.cvtColor(np.array(img_input), cv2.COLOR_RGB2BGR)

            if uploaded_file is not None and model is not None:
                annotated_rgb, persons_count, detections = detect_objects(
                    img_cv, model, conf_threshold,
                    check_helmet=check_helmet, check_vest=check_vest
                )
                workers_list, summary_kpis = analyze_workers_spatial(
                    detections, check_helmet=check_helmet, check_vest=check_vest
                )
                compliance_eval = evaluate_compliance(
                    detections, check_helmet=check_helmet, check_vest=check_vest
                )
                st.image(annotated_rgb, use_container_width=True)
            else:
                st.image(img_input, use_container_width=True)
                is_infraction = ("Infraccion" in sample_name or "1043" in sample_name or "Falta" in sample_name)
                if is_infraction:
                    persons_count = 2
                    summary_kpis = {"total": 2, "compliant": 1, "infractions": 1, "rate": 50.0}
                    compliance_eval = {
                        "status": "danger",
                        "title": "INFRACCIÓN CRÍTICA DETECTADA",
                        "message": "Se detectó personal operando sin Casco de Seguridad.",
                        "category": "Falta de Casco"
                    }
                    workers_list = [
                        {"ID": "#Trabajador-01", "Casco": "NO - Sin Casco (94%)", "Chaleco": "SI (92%)", "Veredicto": "INFRACCION: FALTA CASCO", "Acción Sugerida": "Detener: Colocar Casco"},
                        {"ID": "#Trabajador-02", "Casco": "SI (98%)", "Chaleco": "SI (96%)", "Veredicto": "CUMPLE (EPP Completo)", "Acción Sugerida": "Pase Aprobado"}
                    ]
                else:
                    persons_count = 2
                    summary_kpis = {"total": 2, "compliant": 2, "infractions": 0, "rate": 100.0}
                    compliance_eval = {
                        "status": "safe",
                        "title": "CUMPLIMIENTO NORMATIVO TOTAL",
                        "message": "Todo el personal porta los elementos de protección requeridos.",
                        "category": "Cumplimiento Total (OK)"
                    }
                    workers_list = [
                        {"ID": "#Trabajador-01", "Casco": "SI (99%)", "Chaleco": "SI (95%)", "Veredicto": "CUMPLE (EPP Completo)", "Acción Sugerida": "Pase Aprobado"},
                        {"ID": "#Trabajador-02", "Casco": "SI (97%)", "Chaleco": "SI (94%)", "Veredicto": "CUMPLE (EPP Completo)", "Acción Sugerida": "Pase Aprobado"}
                    ]

        # Estado de Cumplimiento usando render_status_card
        st.markdown(
            render_status_card(
                compliance_eval["status"],
                compliance_eval["title"],
                compliance_eval["message"],
                is_dark=is_dark,
                personnel_count=persons_count
            ),
            unsafe_allow_html=True
        )

        # Desglose de Auditoría por Trabajador
        st.markdown("#### Desglose de Auditoría por Trabajador")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("Operarios en Escena", f"{summary_kpis['total']}")
        m2.metric("Con EPP Completo", f"{summary_kpis['compliant']}")
        m3.metric("En Infracción", f"{summary_kpis['infractions']}")
        m4.metric("Tasa de Cumplimiento", f"{summary_kpis['rate']}%")

        breakdown_data = []
        for w in workers_list:
            breakdown_data.append({
                "ID Sujeto": w["ID"],
                "Casco de Seguridad": w.get("Casco", "N/A"),
                "Chaleco Reflectante": w.get("Chaleco", "N/A"),
                "Veredicto Integral": w.get("Veredicto", "N/A"),
                "Acción Sugerida": w.get("Acción Sugerida", "Verificar")
            })

        df_breakdown = pd.DataFrame(breakdown_data)
        st.dataframe(
            df_breakdown,
            use_container_width=True,
            hide_index=True,
            column_config={
                "ID Sujeto": st.column_config.TextColumn("Operario", width="small"),
                "Casco de Seguridad": st.column_config.TextColumn("Casco", width="medium"),
                "Chaleco Reflectante": st.column_config.TextColumn("Chaleco", width="medium"),
                "Veredicto Integral": st.column_config.TextColumn("Veredicto Forense", width="medium"),
                "Acción Sugerida": st.column_config.TextColumn("Acción Preventiva", width="medium")
            }
        )

    st.markdown("---")
    st.caption("En este modo no se guardan datos en la base de datos.")


# =========================================================
# SECCIÓN 2: ANÁLISIS EN VIVO
# =========================================================
elif "Analisis en Vivo" in page:
    # Controles superiores de cámara en una sola fila compacta
    col_ctrl, col_source, col_mode = st.columns([1.3, 1.8, 1.4])
    with col_ctrl:
        run_camera = st.toggle("Transmisión en Vivo", value=False, help="Conmuta para activar o desactivar la cámara web en tiempo real")
    with col_source:
        camera_source_choice = st.selectbox(
            "Dispositivo de Video:",
            [
                "Cam-0: Integrada / Predeterminada",
                "Cam-1: Webcam Externa USB (Feria)",
                "Cam-2: Dispositivo Secundario USB",
                "Flujo RTSP / IP"
            ],
            index=0,
            help="Selecciona qué cámara física o de red capturará el video."
        )
    with col_mode:
        camera_mode = st.radio(
            "Modo de Video:",
            ["Video Continuo", "Foto Snapshot"],
            horizontal=True
        )

    # Visor de video principal
    if "Video Continuo" in camera_mode:
        custom_stream_url = ""
        if "RTSP / IP" in camera_source_choice:
            custom_stream_url = st.text_input(
                "URL del Flujo RTSP / HTTP de la Cámara:",
                value="http://192.168.1.50:8080/video",
                help="Ingresa la URL del flujo de video (ej. rtsp://... o http://.../video)"
            )

        # Bloque Compacto Centrado: Cámara y Alertas a la par
        col_cam, col_recent = st.columns([0.70, 0.30])
        with col_cam:
            frame_placeholder = st.empty()
        with col_recent:
            recent_slot = st.empty()

        # Pie de Página Compacto: Semáforo + 3 KPIs perfectamente alineados al bloque
        st.markdown("<div style='margin-top: 6px; margin-bottom: 6px;'></div>", unsafe_allow_html=True)
        col_status_card, col_kpi1, col_kpi2, col_kpi3 = st.columns([0.43, 0.19, 0.19, 0.19])

        status_slot = col_status_card.empty()
        kpi1_slot = col_kpi1.empty()
        kpi2_slot = col_kpi2.empty()
        kpi3_slot = col_kpi3.empty()

        # Función auxiliar para renderizar los KPIs y eventos
        def refresh_live_panel(p_count=0, state="standby", title="SISTEMA EN ESPERA", msg="Inicia la transmisión para comenzar la auditoría."):
            status_slot.markdown(render_status_card(state, title, msg, is_dark=is_dark, personnel_count=p_count), unsafe_allow_html=True)
            active_sid = st.session_state.get("current_session_id")
            t_insp, p_pct, _, p_infr = get_compliance_stats(session_id=active_sid)

            kpi1_slot.metric(label="Auditorías", value=f"{t_insp}")
            kpi2_slot.metric(label="Cumplimiento", value=f"{p_pct}%")
            kpi3_slot.metric(label="Infracciones", value=f"{p_infr}")

            with recent_slot.container():
                st.markdown("<div style='font-size:0.75rem; font-weight:700; text-transform:uppercase; margin-bottom:6px; color:var(--brand-primary);'>ÚLTIMAS AUDITORÍAS (TURNO)</div>", unsafe_allow_html=True)
                recent_events = get_recent_incidents(session_id=active_sid, limit=4)
                if recent_events:
                    inc_cards = "".join([render_incident_card(inc["time"], inc["title"], inc["badge"], is_dark) for inc in recent_events])
                    st.markdown(f"<div>{inc_cards}</div>", unsafe_allow_html=True)
                else:
                    st.caption("Esperando eventos en este turno...")

        # Render inicial en standby
        refresh_live_panel(0, "standby", "SISTEMA EN ESPERA", "Inicia la transmisión para comenzar la auditoría.")

        if run_camera:
            if "Cam-0" in camera_source_choice:
                cam_source = 0
                cam_desc = "Cámara 0 (Integrada)"
            elif "Cam-1" in camera_source_choice:
                cam_source = 1
                cam_desc = "Cámara 1 (Externa USB)"
            elif "Cam-2" in camera_source_choice:
                cam_source = 2
                cam_desc = "Cámara 2 (Secundaria)"
            elif "RTSP / IP" in camera_source_choice:
                cam_source = custom_stream_url.strip()
                cam_desc = f"Flujo IP ({custom_stream_url})"
            else:
                cam_source = 0
                cam_desc = "Cámara Predeterminada"

            # Captura en segundo plano desacoplada (Threaded Camera Manager)
            cam_mgr = get_camera_manager()
            cam_stream = cam_mgr.get_stream(cam_source)
            if not cam_stream.is_running:
                if not cam_stream.start():
                    st.error(f"No se pudo conectar a **{cam_desc}**. Verifica que la cámara esté disponible y conectada.")
                    st.stop()

            # Iniciar sesión de auditoría en BD una sola vez
            if "camera_session_id" not in st.session_state:
                st.session_state.camera_session_id = start_camera_session()
                st.session_state.cam_session_events = 0
                st.session_state.cam_session_infractions = 0
                st.session_state.worker_tracker = WorkerTrackManager(
                    infraction_cooldown=45.0, purge_timeout=12.0
                )
                st.session_state.last_panel_time = 0
                st.session_state.prev_persons = -1

            worker_tracker = st.session_state.get("worker_tracker")
            session_id = st.session_state.get("camera_session_id")
            last_panel_time = st.session_state.get("last_panel_time", 0)
            prev_persons = st.session_state.get("prev_persons", -1)

            # Bucle de renderizado fluido
            while run_camera:
                ret, frame = cam_stream.read()
                if not ret or frame is None:
                    time.sleep(0.02)
                    continue

                frame = cv2.flip(frame, 1)

                # Parámetros leídos dinámicamente de config / session_state en cada iteración
                cfg_live = st.session_state.get("config", {})
                ch = cfg_live.get("check_helmet", st.session_state.get("check_helmet", True))
                cv_vest = cfg_live.get("check_vest", st.session_state.get("check_vest", True))
                cur_conf = cfg_live.get("conf_threshold_pct", st.session_state.get("conf_threshold_pct", 45)) / 100.0

                frame_rgb, persons_count, detections = detect_objects(
                    frame, model, cur_conf,
                    check_helmet=ch, check_vest=cv_vest, use_tracking=True
                )
                workers_list, summary_kpis = analyze_workers_spatial(
                    detections, check_helmet=ch, check_vest=cv_vest
                )
                compliance_eval = evaluate_compliance(
                    detections, check_helmet=ch, check_vest=cv_vest
                )

                # Anotar etiquetas de operario sobre cada persona
                for w in workers_list:
                    if "box" in w and len(w["box"]) == 4:
                        bx1, by1, bx2, by2 = [int(coord) for coord in w["box"]]
                        is_ok = w["is_compliant"]
                        tag_color = (0, 220, 110) if is_ok else (0, 60, 240)
                        tag_text = f"{w['ID']} | {'OK' if is_ok else 'INFRACCION'}"
                        tag_w = len(tag_text) * 10
                        if by1 < 45:
                            cv2.rectangle(frame_rgb, (bx1, by1), (bx1 + tag_w, by1 + 22), tag_color, -1)
                            cv2.putText(frame_rgb, tag_text, (bx1 + 4, by1 + 16), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1, cv2.LINE_AA)
                        else:
                            cv2.rectangle(frame_rgb, (bx1, by1 - 24), (bx1 + tag_w, by1), tag_color, -1)
                            cv2.putText(frame_rgb, tag_text, (bx1 + 4, by1 - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1, cv2.LINE_AA)

                # Anotar banner superior HUD
                status_color = (0, 255, 128) if compliance_eval["status"] == "safe" else ((0, 69, 255) if compliance_eval["status"] == "danger" else (0, 200, 255))
                cv2.rectangle(frame_rgb, (0, 0), (frame_rgb.shape[1], 36), (15, 23, 42), -1)
                cv2.putText(frame_rgb, f"REC [MOT TRACKING] | {compliance_eval['title']}", (14, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.58, status_color, 2, cv2.LINE_AA)

                frame_placeholder.image(frame_rgb, channels="RGB", use_container_width=True)

                now = time.time()
                if workers_list and worker_tracker:
                    any_recorded = False
                    for w in workers_list:
                        eval_res = worker_tracker.evaluate_worker_event(w)
                        if eval_res["should_record"]:
                            any_recorded = True
                            conf_val = float(np.mean([d["confidence"] for d in detections])) if detections else 95.0
                            record_camera_audit(
                                category=eval_res["category"],
                                title_detail=eval_res["title"],
                                status=eval_res["status"],
                                personnel_count=persons_count,
                                confidence=round(conf_val, 1),
                                frame_bgr=frame,
                                worker_id=eval_res["worker_id"]
                            )
                            st.session_state.cam_session_events = st.session_state.get("cam_session_events", 0) + 1
                            if eval_res["status"] in ["danger", "warning"]:
                                st.session_state.cam_session_infractions = st.session_state.get("cam_session_infractions", 0) + 1
                            refresh_live_panel(persons_count, eval_res["status"], eval_res["title"], compliance_eval["message"])
                            last_panel_time = now

                    worker_tracker.purge_inactive_tracks()

                    if not any_recorded and ((now - last_panel_time > 1.2) or (persons_count != prev_persons)):
                        refresh_live_panel(persons_count, compliance_eval["status"], compliance_eval["title"], compliance_eval["message"])
                        last_panel_time = now
                else:
                    if worker_tracker:
                        worker_tracker.purge_inactive_tracks()
                    if (now - last_panel_time > 1.5) or (prev_persons > 0):
                        refresh_live_panel(0, "standby", "ZONA DESPEJADA", "No hay personal presente en el encuadre.")
                        last_panel_time = now

                st.session_state.last_panel_time = last_panel_time
                st.session_state.prev_persons = persons_count
                prev_persons = persons_count

                time.sleep(0.02)

        else:
            # Toggle OFF: detener stream de cámara limpiamente
            cam_mgr = get_camera_manager()
            cam_mgr.stop_all()

            # Cerrar sesión de cámara si existía
            if "camera_session_id" in st.session_state:
                end_camera_session(
                    st.session_state.camera_session_id,
                    st.session_state.get("cam_session_events", 0),
                    st.session_state.get("cam_session_infractions", 0)
                )
                for k in ["camera_session_id", "cam_session_events", "cam_session_infractions",
                          "worker_tracker", "last_panel_time", "prev_persons"]:
                    st.session_state.pop(k, None)

            frame_placeholder.info("Activa el switch 'Transmisión en Vivo' para iniciar la detección con YOLOv8.")

    else:
        st.info("Utiliza la cámara de tu dispositivo para capturar una foto instantánea y auditarla.")
        camera_image = st.camera_input("Capturar foto para auditoría de EPP")

        if camera_image is not None:
            img = Image.open(camera_image)
            img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

            annotated_rgb, persons_count, detections = detect_objects(
                img_cv, model, conf_threshold,
                check_helmet=check_helmet, check_vest=check_vest
            )
            compliance_eval = evaluate_compliance(
                detections, check_helmet=check_helmet, check_vest=check_vest
            )

            conf_mean = float(np.mean([d["confidence"] for d in detections])) if detections else 95.0
            record_camera_audit(
                category=compliance_eval["category"] or "Cumplimiento Total (OK)",
                title_detail=f"Cámara Dispositivo: {compliance_eval['title']}",
                status=compliance_eval["status"],
                personnel_count=persons_count,
                confidence=round(conf_mean, 1),
                frame_bgr=img_cv
            )

            st.image(annotated_rgb, caption="Resultado de la Auditoría en Vivo", use_container_width=True)

            col1, col2 = st.columns(2)
            with col1:
                st.markdown(
                    render_status_card(
                        compliance_eval["status"],
                        compliance_eval["title"],
                        compliance_eval["message"],
                        is_dark=is_dark,
                        personnel_count=persons_count
                    ),
                    unsafe_allow_html=True
                )
            with col2:
                total_inspections, pct, _, infractions = get_compliance_stats(session_id=st.session_state.get('current_session_id'))
                st.metric(label="Cumplimiento en Turno", value=f"{pct}%", delta=f"{persons_count} personas detectadas")


# =========================================================
# SECCIÓN 3: ESTADÍSTICAS Y CONTROL DE PROCESOS
# =========================================================
elif "Estadisticas" in page:
    st.markdown("### Estadísticas y Control de Procesos")
    st.caption("Métricas del análisis en vivo. Solo refleja datos de sesiones registradas.")

    # Selector de sesión
    sessions = get_all_sessions_list()
    session_options = {"Histórico Global Consolidado": None}
    for s in sessions:
        label = f"Sesión #{s['id']} ({s.get('start_time', '')}) - {s.get('total_events', 0)} eventos"
        session_options[label] = s['id']

    selected_label = st.selectbox("Seleccionar Sesión / Turno para Análisis:", list(session_options.keys()))
    selected_session = session_options[selected_label]

    total_inspections, pct, compliance_rate, total_infractions = get_compliance_stats(session_id=selected_session)
    roi_default = calculate_roi(120, 2500)

    # 4 KPI Cards Ejecutivas
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    kpi_label = f"Auditorías (Sesión #{selected_session})" if selected_session else "Total Auditorías Históricas"
    infraction_pct = round((total_infractions / total_inspections * 100), 1) if total_inspections > 0 else 0

    kpi1.metric(label=kpi_label, value=f"{total_inspections:,}", delta=f"{infraction_pct}% infracciones")
    kpi2.metric(label="% Cumplimiento", value=f"{compliance_rate}%", delta=f"{compliance_rate - 75:.1f}% vs media industrial")
    kpi3.metric(label="Total Infracciones", value=f"{total_infractions}", delta=f"{infraction_pct}% tasa crítica")
    kpi4.metric(label="ROI Estimado Anual", value=f"${roi_default['total_saved']:,.0f} USD", delta=f"ROI +{roi_default['roi_percent']:.0f}%")

    st.markdown("---")

    # Gráficos y Tendencias (Control Estadístico ISO 45001 / OSHA)
    col_chart1, col_chart2 = st.columns([1.1, 1.3])

    with col_chart1:
        st.markdown("#### Distribución de Severidad y Cumplimiento EPP")
        chart_df = get_history_dataframe(session_id=selected_session)
        fig_bars = create_severity_bar_chart(chart_df, is_dark=is_dark)
        st.plotly_chart(fig_bars, use_container_width=True, config={"displayModeBar": False})
        st.caption("*Desglose semafórico y frecuencia de eventos por categoría.*")

    with col_chart2:
        st.markdown("#### Gráfico de Control Estadístico Horario (SPC)")
        hours_data = get_hourly_risk_distribution(session_id=selected_session)
        fig_spc = create_spc_control_chart(hours_data, is_dark=is_dark)
        st.plotly_chart(fig_spc, use_container_width=True, config={"displayModeBar": False})
        st.caption("*Límites de control estadístico (UCL/CL) y picos de riesgo (ISO 45001 / OSHA).*")

    st.markdown("---")

    # Calculadora Interactiva de ROI
    st.markdown("#### Calculadora Interactiva de Retorno de Inversión (ROI)")
    st.write("Ajusta las variables operativas de la planta para estimar el ahorro anual con **Vigilante EPP**.")

    col_inputs, col_results = st.columns([1.1, 1.2])

    with col_inputs:
        num_workers = st.slider("Trabajadores en Planta / Turno:", min_value=1, max_value=200, value=50, step=5)
        avg_fine = st.slider("Costo promedio por multa o incidente laboral (USD):", min_value=500, max_value=10000, value=2500, step=250)
        roi = calculate_roi(num_workers, avg_fine)

    with col_results:
        res_col1, res_col2 = st.columns(2)
        with res_col1:
            st.metric(
                label="Accidentes Evitados / Año",
                value=f"{roi['saved_incidents']}",
                delta="85% tasa de reducción"
            )
        with res_col2:
            st.metric(
                label="Ahorro Anual Estimado",
                value=f"${roi['total_saved']:,.0f} USD",
                delta=f"ROI Neto: +{roi['roi_percent']:.0f}%"
            )

        st.markdown(f"""
        > **Resumen Ejecutivo:** Con una dotación de **{num_workers} operarios**, Vigilante EPP proyecta evitar **~{roi['saved_incidents']} incidentes anuales**, generando un ahorro estimado de **${roi['total_saved']:,.2f} USD** en multas laborales y primas de seguro.
        """)


# =========================================================
# SECCIÓN 4: REPORTES Y EXPORTACIÓN
# =========================================================
elif "Reportes" in page:
    st.markdown("### Reportes y Exportación")
    st.caption("Dictamen pericial automatizado con trazabilidad por operario, peritaje fotográfico y exportación oficial (ISO 45001 / OSHA).")

    # Selector de sesión
    sessions = get_all_sessions_list()
    session_options = {"Histórico Global Consolidado": None}
    for s in sessions:
        label = f"Sesión #{s['id']} ({s.get('start_time', '')}) - {s.get('total_events', 0)} eventos"
        session_options[label] = s['id']

    col_rep_sess, col_rep_auditor = st.columns([1.5, 1.5])
    with col_rep_sess:
        selected_label = st.selectbox("Seleccionar Sesión para Reporte:", list(session_options.keys()))
        selected_session = session_options[selected_label]
    with col_rep_auditor:
        auditor_name = st.text_input("Nombre del Auditor / Perito:", value="Supervisor SST")

    detailed_df = get_detailed_events_dataframe(session_id=selected_session)

    if detailed_df.empty:
        st.info("No hay datos registrados. Usa la sección Análisis en Vivo para comenzar.")
    else:
        audit_kpis = compute_audit_kpis(detailed_df)

        # Tarjeta de Diagnóstico Pericial
        v_color = "#10b981" if audit_kpis["risk_badge"] == "safe" else ("#ef4444" if audit_kpis["risk_badge"] == "danger" else "#f59e0b")
        st.markdown(f"""
        <div style="background: rgba(23, 31, 51, 0.4); border: 1px solid #424754; border-left: 6px solid {v_color}; border-radius: 8px; padding: 14px 18px; margin-bottom: 16px;">
            <div style="font-size:0.75rem; font-weight:700; color:{v_color}; text-transform:uppercase; letter-spacing:0.04em;">DIAGNÓSTICO PERICIAL DE AUDITORÍA</div>
            <div style="font-size:1.1rem; font-weight:800; color:#f8fafc; margin: 4px 0;">{audit_kpis['risk_verdict']}</div>
            <div style="font-size:0.82rem; color:#cbd5e1;">Infracción predominante: <strong style="color:#f8fafc;">{audit_kpis['top_infraction']}</strong> &bull; Total de verificaciones: <strong style="color:#f8fafc;">{audit_kpis['total_inspections']}</strong> &bull; Apego a la norma: <strong style="color:{v_color};">{audit_kpis['compliance_pct']}%</strong></div>
        </div>
        """, unsafe_allow_html=True)

        # Filtros Interactivos del Informe
        col_f1, col_f2 = st.columns([1.5, 1.5])
        with col_f1:
            filter_severity = st.selectbox(
                "Filtrar por nivel de riesgo:",
                ["Todos los registros", "Solo Infracciones (Crítico / Advertencia)", "Solo Cumplimientos (Seguro)"]
            )
        with col_f2:
            all_workers = ["Todos los operarios"]
            if not detailed_df.empty and "ID_Operario" in detailed_df.columns:
                unique_w = [w for w in detailed_df["ID_Operario"].dropna().unique().tolist() if w != "N/A"]
                unique_w.sort()
                all_workers.extend(unique_w)
            filter_worker = st.selectbox("Filtrar por operario rastreado:", all_workers)

        filtered_df = detailed_df.copy()
        if "Solo Infracciones" in filter_severity:
            filtered_df = filtered_df[filtered_df["Nivel_Riesgo"].isin(["danger", "warning"])]
        elif "Solo Cumplimientos" in filter_severity:
            filtered_df = filtered_df[filtered_df["Nivel_Riesgo"] == "safe"]

        if filter_worker != "Todos los operarios":
            filtered_df = filtered_df[filtered_df["ID_Operario"] == filter_worker]

        # Bitácora Forense Filtrada
        if not filtered_df.empty:
            col_vm1, col_vm2 = st.columns([1.6, 1.4])
            with col_vm1:
                st.markdown(f"**Registros coincidentes:** `{len(filtered_df)} eventos periciales`")
            with col_vm2:
                view_mode = st.radio(
                    "Modalidad de visualización:",
                    ["Tabla Ejecutiva (ISO 45001)", "Tarjetas Periciales (Feed)"],
                    horizontal=True,
                    label_visibility="collapsed"
                )

            if "Tabla" in view_mode:
                display_df = filtered_df.copy()
                risk_map = {
                    "safe": "CONFORME",
                    "warning": "ADVERTENCIA",
                    "danger": "CRÍTICO"
                }
                display_df["Nivel_Riesgo"] = display_df["Nivel_Riesgo"].map(lambda x: risk_map.get(str(x).lower(), str(x)))
                if "ID_Evento" in display_df.columns:
                    display_df["ID_Evento"] = display_df["ID_Evento"].apply(lambda x: f"#EV-{int(x):04d}" if pd.notna(x) else "")
                if "Certeza_Pct" in display_df.columns:
                    display_df["Certeza_Pct"] = display_df["Certeza_Pct"].apply(lambda x: f"{float(x):.1f}%" if pd.notna(x) else "95.0%")

                cols_to_show = [c for c in ["ID_Evento", "Sesion", "ID_Operario", "Fecha_Hora", "Categoria", "Detalle_Auditoria", "Nivel_Riesgo", "Certeza_Pct"] if c in display_df.columns]

                st.dataframe(
                    display_df[cols_to_show],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "ID_Evento": st.column_config.TextColumn("Código", width="small"),
                        "Sesion": st.column_config.TextColumn("Turno / Sesión", width="medium"),
                        "ID_Operario": st.column_config.TextColumn("Operario", width="small"),
                        "Fecha_Hora": st.column_config.DatetimeColumn("Fecha y Hora", format="DD/MM/YYYY HH:mm:ss", width="medium"),
                        "Categoria": st.column_config.TextColumn("Categoría EPP", width="medium"),
                        "Detalle_Auditoria": st.column_config.TextColumn("Dictamen Pericial", width="large"),
                        "Nivel_Riesgo": st.column_config.TextColumn("Nivel de Riesgo", width="small"),
                        "Certeza_Pct": st.column_config.TextColumn("Certeza IA", width="small")
                    }
                )
            else:
                card_cols = st.columns(2)
                bg_card_hex = "#171f33" if is_dark else "#ffffff"
                text_main = "#f8fafc" if is_dark else "#0f172a"
                text_sub = "#94a3b8" if is_dark else "#64748b"
                border_dark = "#424754" if is_dark else "#cbd5e1"

                for idx, (_, row) in enumerate(filtered_df.iterrows()):
                    col = card_cols[idx % 2]
                    r_status = str(row.get("Nivel_Riesgo", "safe")).lower()
                    b_color = "#10b981" if r_status == "safe" else ("#ef4444" if r_status == "danger" else "#f59e0b")
                    b_bg = "rgba(16, 185, 129, 0.15)" if r_status == "safe" else ("rgba(239, 68, 68, 0.15)" if r_status == "danger" else "rgba(245, 158, 11, 0.15)")
                    b_text = "CONFORME" if r_status == "safe" else ("CRÍTICO" if r_status == "danger" else "ADVERTENCIA")

                    img_path = str(row.get("Ruta_Evidencia", "") or "")
                    has_img = os.path.exists(img_path) if img_path else False

                    with col:
                        st.markdown(f"""
                        <div style="background:{bg_card_hex}; border:1px solid {border_dark}; border-left:5px solid {b_color}; border-radius:8px; padding:12px 14px; margin-bottom:12px;">
                            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                                <span style="font-size:0.75rem; font-family:monospace; font-weight:700; color:{text_sub};">#EV-{int(row.get('ID_Evento', 0)):04d} &bull; {row.get('Fecha_Hora', '')}</span>
                                <span style="background:{b_bg}; color:{b_color}; border:1px solid {b_color}; font-size:0.68rem; font-weight:800; padding:2px 8px; border-radius:4px;">{b_text}</span>
                            </div>
                            <div style="font-size:0.94rem; font-weight:800; color:{text_main}; margin-bottom:4px;">
                                {row.get('ID_Operario', 'Operario')} &bull; {row.get('Categoria', '')}
                            </div>
                            <div style="font-size:0.80rem; color:{text_sub}; line-height:1.3;">
                                {row.get('Detalle_Auditoria', '')}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        if has_img:
                            with st.expander(f"Ver Evidencia Fotográfica ({row.get('ID_Operario', 'Operario')})", expanded=False):
                                st.image(img_path, use_container_width=True)
        else:
            st.info("No se encontraron registros que coincidan con los filtros seleccionados.")

        st.markdown("---")
        # Galería de Evidencias Fotográficas de Infracciones
        st.markdown("#### Galería de Evidencias Fotográficas de Infracciones")
        st.caption("Registro visual pericial de capturas fotográficas asociadas a infracciones detectadas por cámara.")

        with st.expander("Desplegar / Ocultar Galería de Evidencias Fotográficas", expanded=True):
            if "Ruta_Evidencia" in detailed_df.columns:
                evidence_rows = detailed_df[detailed_df["Ruta_Evidencia"].notna() & (detailed_df["Ruta_Evidencia"] != "")]
                if not evidence_rows.empty:
                    evidence_cols = st.columns(3)
                    for idx, (_, ev_row) in enumerate(evidence_rows.head(6).iterrows()):
                        col = evidence_cols[idx % 3]
                        img_path = ev_row["Ruta_Evidencia"]
                        if os.path.exists(img_path):
                            caption_text = f"{ev_row.get('ID_Operario', 'Operario')} - {ev_row.get('Categoria', '')}\n{ev_row.get('Fecha_Hora', '')}"
                            col.image(img_path, caption=caption_text, use_container_width=True)
                else:
                    st.info("No hay evidencias fotográficas registradas en este periodo.")
            else:
                st.info("No hay evidencias fotográficas registradas aún.")

        st.markdown("---")
        # Exportación Formal de Informes
        st.markdown("#### Exportación Oficial de Informes y Certificados")

        col_exp1, col_exp2, col_exp3 = st.columns(3)
        with col_exp1:
            session_display = f"Sesión #{selected_session}" if selected_session else "Histórico Global Consolidado"
            html_report = generate_html_report(filtered_df, session_name=session_display, auditor_name=auditor_name)
            html_filename = f"informe_auditoria_epp_{datetime.date.today()}.html"
            st.download_button(
                label="Descargar Informe Oficial (PDF)",
                data=html_report.encode("utf-8"),
                file_name=html_filename,
                mime="text/html",
                use_container_width=True,
                help="Descarga el informe oficial en formato HTML con membrete, listo para guardar en PDF con Ctrl+P"
            )
        with col_exp2:
            forensic_csv = filtered_df.to_csv(index=False).encode('utf-8')
            csv_name = f"vigilante_epp_sesion_{selected_session}_{datetime.date.today()}.csv" if selected_session else f"vigilante_epp_historico_{datetime.date.today()}.csv"
            st.download_button(
                label="Descargar Bitácora Forense (.CSV)",
                data=forensic_csv,
                file_name=csv_name,
                mime="text/csv",
                use_container_width=True
            )
        with col_exp3:
            chart_df = get_history_dataframe(session_id=selected_session)
            summary_csv = chart_df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Descargar Resumen Consolidado (.CSV)",
                data=summary_csv,
                file_name=f"vigilante_epp_resumen_kpis_{datetime.date.today()}.csv",
                mime="text/csv",
                use_container_width=True
            )
