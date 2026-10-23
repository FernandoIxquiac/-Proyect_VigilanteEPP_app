import time
import threading
import cv2
import numpy as np

from .camera import get_camera_manager
from .detector import detect_objects, analyze_workers_spatial, evaluate_compliance
from .native_viewer import LatestFrameNativeViewer
from .tracker_manager import WorkerTrackManager


def annotate_auditor_frame(frame_bgr, workers_list, compliance_eval, hud_prefix="REC [MOT TRACKING]"):
    """
    Dibuja cajas delimitadoras con etiquetas de operarios y banner superior HUD en el fotograma BGR.
    """
    for w in workers_list:
        if "box" in w and len(w["box"]) == 4:
            bx1, by1, bx2, by2 = [int(coord) for coord in w["box"]]
            is_ok = w.get("is_compliant", False)
            tag_color = (0, 220, 110) if is_ok else (0, 60, 240)
            tag_text = f"{w.get('ID', 'Operario')} | {'OK' if is_ok else 'INFRACCIÓN'}"
            tag_w = len(tag_text) * 10
            if by1 < 45:
                cv2.rectangle(frame_bgr, (bx1, by1), (bx1 + tag_w, by1 + 22), tag_color, -1)
                cv2.putText(frame_bgr, tag_text, (bx1 + 4, by1 + 16), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1, cv2.LINE_AA)
            else:
                cv2.rectangle(frame_bgr, (bx1, by1 - 24), (bx1 + tag_w, by1), tag_color, -1)
                cv2.putText(frame_bgr, tag_text, (bx1 + 4, by1 - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 0), 1, cv2.LINE_AA)

    h_frame, w_frame = frame_bgr.shape[:2]
    if h_frame >= 60:
        c_status = compliance_eval.get("status", "safe")
        status_color = (0, 255, 128) if c_status == "safe" else (
            (0, 69, 255) if c_status == "danger" else (0, 200, 255)
        )
        cv2.rectangle(frame_bgr, (0, 0), (w_frame, 36), (42, 23, 15), -1)
        hud_title = compliance_eval.get("title", "AUDITORÍA EN VIVO")
        cv2.putText(frame_bgr, f"{hud_prefix} | {hud_title}", (14, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, status_color, 2, cv2.LINE_AA)

    return frame_bgr


class BaseAuditorService:
    """
    Clase base para servicios de auditoría e inferencia visual continua.
    Gestiona el ciclo de vida del hilo demonio, captura de cámara, pacing de FPS,
    anotación en BGR y sincronización con LatestFrameNativeViewer.
    """
    def __init__(self, window_name: str = "VIGILANTE EPP"):
        self._lock = threading.Lock()
        self._running = False
        self._thread = None
        self._run_id = 0
        self._source = 0
        self._source_desc = "Cámara Predeterminada"
        self._model = None
        self._conf_threshold = 0.45
        self._check_helmet = True
        self._check_vest = True
        self._window_name = window_name
        self._viewer = self._create_native_viewer(self._window_name)
        self._native_viewer = self._viewer
        self._worker_tracker = self._create_track_manager()
        self._frame_id = 0

    def _create_native_viewer(self, window_name: str):
        return LatestFrameNativeViewer(window_name)

    def _create_track_manager(self):
        return WorkerTrackManager(infraction_cooldown=45.0, purge_timeout=12.0)

    def _get_camera_manager(self):
        return get_camera_manager()

    def _detect_objects(self, frame, model, conf_threshold, check_helmet, check_vest, use_tracking=True):
        return detect_objects(
            frame, model, conf_threshold,
            check_helmet=check_helmet, check_vest=check_vest,
            use_tracking=use_tracking, return_rgb=False
        )

    def _analyze_workers_spatial(self, detections, check_helmet, check_vest):
        return analyze_workers_spatial(detections, check_helmet=check_helmet, check_vest=check_vest)

    def _evaluate_compliance(self, detections, check_helmet, check_vest):
        return evaluate_compliance(detections, check_helmet=check_helmet, check_vest=check_vest)

    def is_running(self) -> bool:
        with self._lock:
            return self._running

    def is_busy(self) -> bool:
        with self._lock:
            return self._running or (
                self._thread is not None and self._thread.is_alive()
            )

    def _is_active(self, run_id: int) -> bool:
        with self._lock:
            return self._running and self._run_id == run_id

    def _is_run_active(self, run_id: int) -> bool:
        return self._is_active(run_id)

    @staticmethod
    def _pacing_sleep(loop_start: float, target_time: float = 0.045):
        elapsed = time.monotonic() - loop_start
        time.sleep(max(0.015, target_time - elapsed))

    def _acquire_camera_stream(self, source, run_id: int, timeout: float = 3.0):
        cam_mgr = self._get_camera_manager()
        if not self._is_active(run_id):
            return None, False
        stream = cam_mgr.get_stream(source)
        if not self._is_active(run_id):
            return None, False
        started = stream.start()
        release_deadline = time.monotonic() + timeout
        while not started and self._is_active(run_id):
            reader = getattr(stream, "thread", None)
            if reader is None or not reader.is_alive() or time.monotonic() >= release_deadline:
                break
            time.sleep(0.05)
            stream = cam_mgr.get_stream(source)
            started = stream.start()
        return stream, started

    def _on_worker_event_confirmed(self, event_payload: dict, run_id: int):
        raise NotImplementedError
