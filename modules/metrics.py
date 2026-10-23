import streamlit as st
from .database import (
    init_db,
    get_or_create_active_session,
    create_new_session,
    log_camera_event,
)

def init_session_state():
    """Inicializa la base de datos y la sesión activa en Streamlit."""
    init_db()
    if "current_session_id" not in st.session_state:
        st.session_state.current_session_id = get_or_create_active_session()
        
    if "session_events_count" not in st.session_state:
        st.session_state.session_events_count = 0
        
    if "session_infractions_count" not in st.session_state:
        st.session_state.session_infractions_count = 0

def reset_session_state():
    """
    Inicia una nueva sesión limpia sin borrar el historial anterior.
    Preserva todos los datos en la base de datos para auditorías históricas.
    """
    new_session_id = create_new_session()
    st.session_state.current_session_id = new_session_id
    st.session_state.session_events_count = 0
    st.session_state.session_infractions_count = 0
    return new_session_id

def record_camera_audit(category="Cumplimiento Total (OK)", title_detail=None, status="safe", personnel_count=1, confidence=0.0, frame_bgr=None, worker_id="N/A", session_id=None):
    """
    Registra exclusivamente eventos de cámara asociados a la sesión activa en SQLite.
    Es seguro para ser ejecutado desde el hilo de Streamlit o desde hilos desacoplados de fondo.
    """
    target_session_id = session_id
    if target_session_id is None:
        try:
            if "current_session_id" in st.session_state:
                target_session_id = st.session_state.current_session_id
        except Exception:
            target_session_id = None
        
    if target_session_id is None:
        target_session_id = get_or_create_active_session()
        
    event_id = log_camera_event(
        category=category,
        details=title_detail or category,
        status=status,
        personnel_count=personnel_count,
        confidence=confidence,
        frame_bgr=frame_bgr,
        session_id=target_session_id,
        worker_id=worker_id
    )
    
    try:
        if "session_events_count" in st.session_state:
            st.session_state.session_events_count += 1
        if status in ["danger", "warning"] and "session_infractions_count" in st.session_state:
            st.session_state.session_infractions_count += 1
    except Exception:
        pass
        
    return event_id

def calculate_roi(num_workers: int, avg_fine: float):
    """Calcula estimación de retorno de inversión."""
    estimated_infractions = int(num_workers * 0.35)
    saved_incidents = int(estimated_infractions * 0.85)
    total_saved = saved_incidents * avg_fine
    roi_percent = round((total_saved / (avg_fine * 2 + 1) * 10), 1) if avg_fine > 0 else 0
    return {
        "estimated_infractions": estimated_infractions,
        "saved_incidents": saved_incidents,
        "total_saved": total_saved,
        "roi_percent": roi_percent
    }
