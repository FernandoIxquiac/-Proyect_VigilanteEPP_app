import time
import threading
import sqlite3
import cv2
import numpy as np
import streamlit as st

from .auditor_core import BaseAuditorService, annotate_auditor_frame
from .camera import get_camera_manager
from .detector import detect_objects, analyze_workers_spatial, evaluate_compliance
from .tracker_manager import WorkerTrackManager
from .metrics import record_camera_audit
from .audit_writer import AuditEventWriter
from .database import start_camera_session, end_camera_session
from .native_viewer import LatestFrameNativeViewer


class LiveAuditorService(BaseAuditorService):
    """
    Servicio de auditoría continua desacoplado en segundo plano.
    Ejecuta un hilo demonio independiente del ciclo reactivo de Streamlit,
    procesando la inferencia de visión artificial, seguimiento MOT de operarios,
    evaluación espacial de EPP y persistencia transaccional en SQLite sin latencia en la UI.
    """
    def __init__(self):
        super().__init__("VIGILANTE EPP - Monitor de Seguridad Industrial")
        self._show_native_window = False
        self._session_id = None
        self._session_events = 0
        self._session_infractions = 0
        self._audit_writer = None
        self._is_dark = True

        # Estado más reciente accesible de forma segura entre hilos
        self._latest_state = {
            "frame_rgb": None,
            "frame_bytes": None,
            "is_running": False,
            "status": "standby",
            "title": "SISTEMA EN ESPERA",
            "message": "Inicia la transmisión para comenzar la auditoría.",
            "persons_count": 0,
            "workers_list": [],
            "summary_kpis": {"total": 0, "compliant": 0, "infractions": 0, "rate": 100.0},
            "session_id": None,
            "session_events": 0,
            "session_infractions": 0,
            "fps": 0.0,
            "timestamp": 0.0,
            "frame_id": 0,
            "capture_sequence": 0,
            "captured_at": 0.0,
            "processing_started_at": 0.0,
            "processed_at": 0.0,
            "persistence_pending_events": 0,
            "persistence_pending_bytes": 0,
            "persistence_persisted_events": 0,
            "persistence_failed_events": 0,
            "persistence_rejected_events": 0,
            "persistence_last_error": None,
            "show_native_window": False,
            "source_desc": "Cámara Predeterminada"
        }

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

    def _on_worker_event_confirmed(self, event_payload: dict, run_id: int):
        with self._lock:
            if not self._running or run_id != self._run_id:
                return False
            writer = self._audit_writer
            if writer is not None:
                accepted, error = writer.submit(event_payload)
                if not accepted:
                    self._latest_state["persistence_last_error"] = error
                self._sync_persistence_state_locked()
                return accepted
        return False

    def start(self, source=0, source_desc="Cámara Predeterminada", model=None,
              conf_threshold=0.45, check_helmet=True, check_vest=True,
              show_native_window=False) -> bool:
        """
        Inicia el servicio de auditoría en segundo plano.
        Si ya está en ejecución con la misma fuente, actualiza la configuración en vivo.
        """
        with self._lock:
            if self._thread is not None and self._thread.is_alive():
                if not self._running:
                    return False
                self._source = source
                self._source_desc = source_desc
                if model is not None:
                    self._model = model
                self._conf_threshold = float(conf_threshold)
                self._check_helmet = bool(check_helmet)
                self._check_vest = bool(check_vest)
                self._show_native_window = bool(show_native_window)
                request_native = bool(show_native_window)
                already_running = True
            else:
                already_running = False

            if already_running:
                run_id = None
            else:
                if self._audit_writer is not None:
                    if not self._audit_writer.is_drained():
                        self._latest_state["persistence_last_error"] = (
                            "Hay eventos pendientes de persistir; espera el cierre del escritor."
                        )
                        return False
                    if self._session_id is not None:
                        try:
                            end_camera_session(
                                self._session_id,
                                self._session_events,
                                self._session_infractions,
                            )
                        except sqlite3.Error as exc:
                            self._latest_state["persistence_last_error"] = str(exc)
                            return False
                    self._audit_writer = None
                    self._session_id = None
                    self._session_events = 0
                    self._session_infractions = 0

                self._source = source
                self._source_desc = source_desc
                if model is not None:
                    self._model = model
                self._conf_threshold = float(conf_threshold)
                self._check_helmet = bool(check_helmet)
                self._check_vest = bool(check_vest)
                self._show_native_window = bool(show_native_window)
                self._run_id += 1
                run_id = self._run_id
                self._running = True
                self._worker_tracker.reset()
                self._session_id = start_camera_session()
                self._session_events = 0
                self._session_infractions = 0
                self._audit_writer = AuditEventWriter(
                    record_camera_audit,
                    on_result=self._on_audit_write_result,
                )
                self._audit_writer.start()
                self._latest_state.update({
                    "persistence_pending_events": 0,
                    "persistence_pending_bytes": 0,
                    "persistence_persisted_events": 0,
                    "persistence_failed_events": 0,
                    "persistence_rejected_events": 0,
                    "persistence_last_error": None,
                })
                if self._show_native_window:
                    self._native_viewer.request_enabled(True)
                self._thread = threading.Thread(
                    target=self._audit_loop, args=(run_id,), daemon=True
                )
                self._thread.start()

        if already_running:
            self._native_viewer.request_enabled(request_native)
            return True

        return True

    def update_config(self, conf_threshold=None, check_helmet=None, check_vest=None, show_native_window=None):
        """Actualiza parámetros de inspección en tiempo real sin reiniciar la captura."""
        with self._lock:
            if conf_threshold is not None:
                self._conf_threshold = float(conf_threshold)
            if check_helmet is not None:
                self._check_helmet = bool(check_helmet)
            if check_vest is not None:
                self._check_vest = bool(check_vest)
            if show_native_window is not None:
                self._show_native_window = bool(show_native_window)
        if show_native_window is not None:
            self._native_viewer.request_enabled(show_native_window)

    def set_native_window(self, enable: bool):
        """Activa o desactiva la visualización en ventana nativa de escritorio."""
        with self._lock:
            self._show_native_window = bool(enable)
            self._latest_state["show_native_window"] = bool(enable)
        self._native_viewer.request_enabled(enable)

    def set_theme(self, is_dark: bool):
        """Actualiza el tema global visual del auditor."""
        with self._lock:
            self._is_dark = bool(is_dark)

    def get_theme(self) -> bool:
        """Obtiene el tema global visual configurado."""
        with self._lock:
            return self._is_dark

    def stop(self):
        """Detiene el hilo de auditoría y libera recursos de forma segura e inmediata."""
        with self._lock:
            self._running = False
            self._run_id += 1
            self._show_native_window = False
            self._latest_state["is_running"] = False
            self._latest_state["frame_rgb"] = None
            self._latest_state["frame_bytes"] = None
            self._latest_state["capture_sequence"] = 0
            self._latest_state["captured_at"] = 0.0
            self._latest_state["processing_started_at"] = 0.0
            self._latest_state["processed_at"] = 0.0
            self._latest_state["status"] = "standby"
            self._latest_state["title"] = "SISTEMA EN ESPERA"
            self._latest_state["message"] = "Inicia la transmisión para comenzar la auditoría."
            self._latest_state["show_native_window"] = False
            self._latest_state["persons_count"] = 0
            target_thread = self._thread
            sid = self._session_id
            t_events = self._session_events
            t_infr = self._session_infractions
            writer = self._audit_writer

        # Liberar la captura de video de inmediato para desbloquear lecturas
        try:
            self._get_camera_manager().stop_all()
        except Exception:
            pass

        # Cerrar ventana nativa si permanecía abierta
        self._native_viewer.shutdown(timeout=2.0)

        if target_thread is not None and target_thread.is_alive():
            target_thread.join(timeout=1.0)

        drained = writer.close(timeout=5.0) if writer is not None else True
        close_error = None
        if drained and sid:
            with self._lock:
                t_events = self._session_events
                t_infr = self._session_infractions
            try:
                end_camera_session(sid, t_events, t_infr)
            except sqlite3.Error as exc:
                drained = False
                close_error = f"Eventos drenados, pero no se cerró la sesión: {exc}"

        with self._lock:
            if self._thread is None or not self._thread.is_alive():
                self._thread = None
            if drained:
                self._session_id = None
                self._session_events = 0
                self._session_infractions = 0
                self._audit_writer = None
                self._latest_state["session_id"] = None
            else:
                status = writer.get_status() if writer is not None else {}
                pending = status.get("pending_events", 0)
                self._latest_state["persistence_last_error"] = close_error or (
                    f"El guardado no terminó; {pending} evento(s) siguen pendientes."
                )
                self._sync_persistence_state_locked()
            self._latest_state["is_running"] = False
            self._latest_state["frame_rgb"] = None
            self._latest_state["frame_bytes"] = None
            self._latest_state["capture_sequence"] = 0
            self._latest_state["captured_at"] = 0.0
            self._latest_state["processing_started_at"] = 0.0
            self._latest_state["processed_at"] = 0.0
            self._latest_state["status"] = "standby"
            self._latest_state["title"] = "SISTEMA EN ESPERA"
            self._latest_state["message"] = "Inicia la transmisión para comenzar la auditoría."
            self._latest_state["show_native_window"] = False
            self._latest_state["persons_count"] = 0

    def get_latest_state(self) -> dict:
        """
        Retorna una instantánea thread-safe del estado de auditoría más reciente.
        Operación O(1) de memoria no bloqueante.
        """
        with self._lock:
            latest_state = dict(self._latest_state)
            writer = self._audit_writer
        if writer is not None:
            latest_state.update(self._persistence_state(writer.get_status()))
        latest_state["show_native_window"] = self._native_viewer.is_enabled()
        return latest_state

    def _audit_loop(self, run_id=None):
        if run_id is None:
            with self._lock:
                run_id = self._run_id
        try:
            self._audit_loop_impl(run_id)
        finally:
            self._native_viewer.shutdown(timeout=2.0)
            with self._lock:
                writer = self._audit_writer
            if writer is not None:
                drained = writer.close(timeout=5.0)
                if not drained:
                    with self._lock:
                        status = writer.get_status()
                        self._latest_state["persistence_last_error"] = (
                            "El cierre automático no terminó; "
                            f"{status['pending_events']} evento(s) siguen pendientes."
                        )
                        self._sync_persistence_state_locked()
            with self._lock:
                if self._thread is threading.current_thread():
                    self._thread = None

    def _audit_loop_impl(self, run_id=None):
        """
        Ciclo principal de supervisión e inferencia ejecutado en hilo demonio.
        Aísla el cómputo de la cámara y de YOLO de las operaciones de Streamlit.
        """
        if run_id is None:
            with self._lock:
                run_id = self._run_id
        with self._lock:
            source = self._source
            source_desc = self._source_desc

        cam_stream, camera_started = self._acquire_camera_stream(source, run_id)
        with self._lock:
            if not self._running or run_id != self._run_id:
                cancelled = True
            else:
                cancelled = False
                if not camera_started:
                    self._running = False
                    self._latest_state["status"] = "danger"
                    self._latest_state["title"] = "ERROR DE CONEXIÓN DE CÁMARA"
                    reader = getattr(cam_stream, "thread", None) if cam_stream else None
                    if reader is not None and reader.is_alive():
                        self._latest_state["message"] = (
                            "La cámara anterior aún está cerrándose. "
                            "Espera un momento y vuelve a iniciar."
                        )
                    else:
                        self._latest_state["message"] = f"No se pudo acceder a {source_desc}."
        if cancelled:
            if camera_started and cam_stream is not None:
                cam_stream.stop()
            return
        if not camera_started or cam_stream is None:
            return

        fps_timer = time.monotonic()
        fps_counter = 0
        current_fps = 0.0
        first_frame_pending = True
        last_capture_sequence = None

        while self._is_run_active(run_id):
            loop_start = time.monotonic()

            capture_reader = getattr(cam_stream, "read_with_metadata", None)
            if capture_reader is not None:
                ret, frame, capture_sequence, captured_at = capture_reader()
            else:
                ret, frame = cam_stream.read()
                capture_sequence = (
                    1 if last_capture_sequence is None
                    else last_capture_sequence + 1
                )
                captured_at = time.monotonic()
            if not ret or frame is None:
                if not getattr(cam_stream, "is_running", True):
                    with self._lock:
                        if self._running and run_id == self._run_id:
                            self._running = False
                            self._frame_id += 1
                            self._latest_state.update({
                                "frame_rgb": None,
                                "frame_bytes": None,
                                "is_running": False,
                                "status": "danger",
                                "title": "CONEXIÓN DE CÁMARA PERDIDA",
                                "message": f"Se perdió la conexión con {self._source_desc}.",
                                "persons_count": 0,
                                "workers_list": [],
                                "frame_id": self._frame_id,
                                "capture_sequence": last_capture_sequence or 0,
                                "captured_at": 0.0,
                                "processing_started_at": 0.0,
                                "processed_at": time.monotonic(),
                                "timestamp": time.time(),
                            })
                    break
                time.sleep(0.02)
                continue
            if capture_sequence == last_capture_sequence:
                time.sleep(0.005)
                continue
            last_capture_sequence = capture_sequence
            processing_started_at = time.monotonic()

            # Inversión horizontal para modo espejo natural
            frame = cv2.flip(frame, 1)

            # Lectura sincronizada de parámetros de inspección
            with self._lock:
                if not self._running or run_id != self._run_id:
                    break
                cur_conf = self._conf_threshold
                ch = self._check_helmet
                cv_vest = self._check_vest
                show_native = self._show_native_window
                cur_model = self._model
                current_session_id = self._session_id

            if first_frame_pending:
                with self._lock:
                    if not self._running or run_id != self._run_id:
                        break
                    self._frame_id += 1
                    self._latest_state.update({
                        "frame_rgb": None,
                        "frame_bytes": None,
                        "is_running": True,
                        "status": "initializing",
                        "title": "INICIALIZANDO DETECCIÓN",
                        "message": "Primera imagen recibida. El análisis de EPP está iniciando.",
                        "persons_count": 0,
                        "workers_list": [],
                        "timestamp": time.time(),
                        "frame_id": self._frame_id,
                        "capture_sequence": capture_sequence,
                        "captured_at": captured_at,
                        "processing_started_at": processing_started_at,
                        "processed_at": time.monotonic(),
                        "show_native_window": show_native,
                        "source_desc": self._source_desc,
                    })

                with self._lock:
                    if not self._running or run_id != self._run_id:
                        break
                preview_sequence = self._native_viewer.publish(frame)
                if show_native:
                    self._native_viewer.request_enabled(True)
                    self._native_viewer.wait_until_presented(
                        preview_sequence, timeout=2.0
                    )
                first_frame_pending = False

            with self._lock:
                if not self._running or run_id != self._run_id:
                    break

            # Inferencia YOLO con Tracking de Objetos Multi-Operario (MOT) en BGR nativo
            frame_bgr, persons_count, detections = self._detect_objects(
                frame, cur_model, cur_conf,
                check_helmet=ch, check_vest=cv_vest, use_tracking=True
            )
            with self._lock:
                if not self._running or run_id != self._run_id:
                    break
            workers_list, summary_kpis = self._analyze_workers_spatial(
                detections, check_helmet=ch, check_vest=cv_vest
            )
            compliance_eval = self._evaluate_compliance(
                detections, check_helmet=ch, check_vest=cv_vest
            )

            # Anotación unificada en BGR
            annotate_auditor_frame(frame_bgr, workers_list, compliance_eval, hud_prefix="REC [MOT TRACKING]")

            now = time.monotonic()

            # Evaluación individual por operario con anti-parpadeo y cooldown
            if workers_list and self._worker_tracker:
                for w in workers_list:
                    eval_res = self._worker_tracker.evaluate_worker_event(w)
                    if eval_res["should_record"] and self._is_run_active(run_id):
                        conf_val = float(np.mean([d["confidence"] for d in detections])) if detections else 95.0
                        event_payload = {
                            "category": eval_res["category"],
                            "title_detail": eval_res["title"],
                            "status": eval_res["status"],
                            "personnel_count": persons_count,
                            "confidence": round(conf_val, 1),
                            "frame_bgr": frame,
                            "session_id": current_session_id,
                            "worker_id": eval_res["worker_id"],
                        }
                        self._on_worker_event_confirmed(event_payload, run_id)

                self._worker_tracker.purge_inactive_tracks()

            # Cálculo de tasa de fotogramas (FPS)
            fps_counter += 1
            if now - fps_timer >= 1.0:
                current_fps = round(fps_counter / (now - fps_timer), 1)
                fps_counter = 0
                fps_timer = now

            if (self._is_run_active(run_id) and
                    self._native_viewer.is_enabled()):
                self._native_viewer.publish(frame_bgr)

            # Determinación de estado para tarjeta de estado y UI
            if persons_count == 0:
                display_status = "standby"
                display_title = "ZONA DESPEJADA"
                display_msg = "No se detecta presencia de personal en el encuadre."
            else:
                display_status = compliance_eval.get("status", "safe")
                display_title = compliance_eval.get("title", "SUPERVISIÓN ACTIVA")
                display_msg = compliance_eval.get("message", "Operarios monitoreados.")

            # Publicación thread-safe del estado actual
            with self._lock:
                if not self._running or run_id != self._run_id:
                    break
                published_at = time.time()
                self._frame_id += 1
                self._latest_state["frame_rgb"] = None
                self._latest_state["frame_bytes"] = None
                self._latest_state["is_running"] = True
                self._latest_state["status"] = display_status
                self._latest_state["title"] = display_title
                self._latest_state["message"] = display_msg
                self._latest_state["persons_count"] = persons_count
                self._latest_state["workers_list"] = workers_list
                self._latest_state["summary_kpis"] = summary_kpis
                self._latest_state["session_id"] = current_session_id
                self._latest_state["session_events"] = self._session_events
                self._latest_state["session_infractions"] = self._session_infractions
                self._latest_state["fps"] = current_fps
                self._latest_state["timestamp"] = published_at
                self._latest_state["frame_id"] = self._frame_id
                self._latest_state["capture_sequence"] = capture_sequence
                self._latest_state["captured_at"] = captured_at
                self._latest_state["processing_started_at"] = processing_started_at
                self._latest_state["processed_at"] = time.monotonic()
                self._latest_state["show_native_window"] = self._show_native_window
                self._latest_state["source_desc"] = self._source_desc

            self._pacing_sleep(loop_start)

    def _on_audit_write_result(self, event, event_id, error):
        with self._lock:
            if error is not None:
                self._latest_state["persistence_last_error"] = error
            elif event.get("session_id") == self._session_id:
                self._session_events += 1
                if event.get("status") in ("danger", "warning"):
                    self._session_infractions += 1
                self._latest_state["session_events"] = self._session_events
                self._latest_state["session_infractions"] = self._session_infractions
            self._sync_persistence_state_locked()

    @staticmethod
    def _persistence_state(status):
        result = {
            "persistence_pending_events": status["pending_events"],
            "persistence_pending_bytes": status["pending_bytes"],
            "persistence_persisted_events": status["persisted_events"],
            "persistence_failed_events": status["failed_events"],
            "persistence_rejected_events": status["rejected_events"],
        }
        if status["last_error"] is not None:
            result["persistence_last_error"] = status["last_error"]
        return result

    def _sync_persistence_state_locked(self):
        if self._audit_writer is not None:
            self._latest_state.update(
                self._persistence_state(self._audit_writer.get_status())
            )


@st.cache_resource
def get_live_auditor():
    """
    Retorna la instancia singleton del servicio de auditoría en segundo plano.
    Sobrevive a las re-ejecuciones de Streamlit manteniendo el hilo de inferencia activo.
    """
    return LiveAuditorService()
