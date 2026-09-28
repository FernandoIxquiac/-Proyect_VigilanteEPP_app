import streamlit as st
import pandas as pd
from .database import (
    init_db,
    get_or_create_active_session,
    create_new_session,
    log_camera_event,
    get_compliance_stats as db_get_compliance_stats,
    get_recent_incidents as db_get_recent_incidents,
    get_history_dataframe as db_get_history_dataframe,
    get_detailed_events_dataframe as db_get_detailed_events_dataframe,
    get_hourly_risk_distribution as db_get_hourly_risk_distribution,
    get_all_sessions_list as db_get_all_sessions_list
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

def record_camera_audit(category="Cumplimiento Total (OK)", title_detail=None, status="safe", personnel_count=1, confidence=0.0, frame_bgr=None, worker_id="N/A"):
    """
    Registra exclusivamente eventos de cámara asociados a la sesión activa en SQLite.
    """
    if "current_session_id" not in st.session_state:
        st.session_state.current_session_id = get_or_create_active_session()
        
    session_id = st.session_state.current_session_id
    
    event_id = log_camera_event(
        category=category,
        details=title_detail or category,
        status=status,
        personnel_count=personnel_count,
        confidence=confidence,
        frame_bgr=frame_bgr,
        session_id=session_id,
        worker_id=worker_id
    )
    
    st.session_state.session_events_count += 1
    if status in ["danger", "warning"]:
        st.session_state.session_infractions_count += 1
        
    return event_id

def record_audit(category="Cumplimiento Total (OK)", title_detail=None):
    badge = "safe" if "OK" in category or "Cumplimiento" in category else ("danger" if "Casco" in category else "warning")
    return record_camera_audit(category=category, title_detail=title_detail, status=badge)

def get_compliance_stats(session_id=None):
    """Obtiene estadísticas de cumplimiento (por sesión o global)."""
    return db_get_compliance_stats(session_id=session_id)

def get_recent_incidents(session_id=None, limit=5):
    """Obtiene los incidentes más recientes para el HUD."""
    return db_get_recent_incidents(session_id=session_id, limit=limit)

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

def get_history_dataframe(session_id=None) -> pd.DataFrame:
    """Devuelve las categorías agregadas para gráficas (por sesión o global)."""
    return db_get_history_dataframe(session_id=session_id)

def get_detailed_events_dataframe(session_id=None) -> pd.DataFrame:
    """Devuelve la bitácora completa forense con nombre de sesión."""
    return db_get_detailed_events_dataframe(session_id=session_id)

def get_hourly_risk_distribution(session_id=None) -> pd.DataFrame:
    """Devuelve la distribución horaria de infracciones."""
    return db_get_hourly_risk_distribution(session_id=session_id)

def get_all_sessions_list():
    """Obtiene el listado de todas las sesiones registradas."""
    return db_get_all_sessions_list()
