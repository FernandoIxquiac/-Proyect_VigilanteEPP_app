# Package initialization for modules
from .detector import load_detector_model, detect_objects, evaluate_compliance, analyze_workers_spatial, CLASS_TRANSLATIONS
from .metrics import (
    init_session_state,
    reset_session_state,
    record_audit,
    record_camera_audit,
    get_compliance_stats,
    get_recent_incidents,
    calculate_roi,
    get_history_dataframe,
    get_detailed_events_dataframe,
    get_hourly_risk_distribution,
    get_all_sessions_list
)
from .database import (
    get_or_create_active_session,
    create_new_session,
    update_session_counters,
    start_camera_session,
    end_camera_session,
    clear_all_data
)
from .tracker_manager import WorkerTrackManager
from .report_generator import compute_audit_kpis, generate_html_report
from .samples import generate_demo_sample
from .camera import ThreadedCamera, CameraStreamManager, get_camera_manager
