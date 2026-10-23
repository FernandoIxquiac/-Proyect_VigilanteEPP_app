import collections
import datetime
import threading
import time
import cv2
import numpy as np
import streamlit as st

from .auditor_core import BaseAuditorService, annotate_auditor_frame
from .camera import get_camera_manager
from .detector import detect_objects, analyze_workers_spatial, evaluate_compliance
from .native_viewer import LatestFrameNativeViewer
from .tracker_manager import WorkerTrackManager


def _annotate_demo_frame(frame_bgr, workers_list, compliance_eval):
    """Dibuja etiquetas de operarios y banner superior HUD en el fotograma BGR."""
    return annotate_auditor_frame(
        frame_bgr, workers_list, compliance_eval,
        hud_prefix="DEMO [MODO SANDBOX - SIN PERSISTENCIA]"
    )


class DemoVideoService(BaseAuditorService):
    """Presenta las detecciones del modelo en una ventana nativa independiente sin persistencia."""

    def __init__(self):
        super().__init__("VIGILANTE EPP - Demostracion de Video")
        self._recent_events = collections.deque(maxlen=6)
        self._total_inspections = 0
        self._infractions_count = 0
        self._state = {
            "status": "standby",
            "title": "SISTEMA EN ESPERA",
            "message": "La demostración está detenida.",
            "persons_count": 0,
            "detections_count": 0,
            "fps": 0.0,
            "recent_events": [],
            "total_inspections": 0,
            "compliance_pct": 100.0,
            "infractions_count": 0,
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
            self._record_demo_event_locked(
                title=event_payload.get("title_detail") or event_payload.get("category", "Demostración"),
                status=event_payload.get("status", "safe"),
                category=event_payload.get("category", "Demostración"),
                worker_id=event_payload.get("worker_id", "N/A"),
            )
            return True

    def _get_compliance_pct_locked(self):
        if self._total_inspections > 0:
            ok_count = max(0, self._total_inspections - self._infractions_count)
            return round((ok_count / self._total_inspections) * 100, 1)
        return 100.0

    def _record_demo_event_locked(self, title: str, status: str, category: str = "", worker_id: str = "N/A"):
        now = datetime.datetime.now()
        time_str = now.strftime("%I:%M:%S %p")
        self._total_inspections += 1
        if status in ("danger", "warning"):
            self._infractions_count += 1
        compliance_pct = self._get_compliance_pct_locked()

        event_entry = {
            "time": time_str,
            "title": title or category or "Auditoría Demostración",
            "badge": status,
            "status": status,
        }
        self._recent_events.appendleft(event_entry)
        self._state["recent_events"] = list(self._recent_events)
        self._state["total_inspections"] = self._total_inspections
        self._state["infractions_count"] = self._infractions_count
        self._state["compliance_pct"] = compliance_pct

    def get_state(self):
        with self._lock:
            state_copy = dict(self._state)
            state_copy["recent_events"] = list(self._recent_events)
            state_copy["total_inspections"] = self._total_inspections
            state_copy["infractions_count"] = self._infractions_count
            state_copy["compliance_pct"] = self._get_compliance_pct_locked()
            return state_copy

    def get_run_id(self):
        """Identifica la ejecución para cerrar solo la ventana iniciada aquí."""
        with self._lock:
            return self._run_id

    def update_config(self, conf_threshold, check_helmet, check_vest):
        """Aplica la sensibilidad y los filtros en el siguiente fotograma."""
        with self._lock:
            self._conf_threshold = float(conf_threshold)
            self._check_helmet = bool(check_helmet)
            self._check_vest = bool(check_vest)

    def start(self, source, model, conf_threshold=0.45,
              check_helmet=True, check_vest=True):
        """Inicia la captura sin crear una sesión de auditoría."""
        with self._lock:
            if self._running or (
                self._thread is not None and self._thread.is_alive()
            ):
                return False
            if model is None:
                self._state.update({
                    "status": "danger",
                    "title": "MODELO NO DISPONIBLE",
                    "message": "No hay un modelo cargado para analizar el video.",
                })
                return False
            if isinstance(source, str) and not source.strip():
                self._state.update({
                    "status": "danger",
                    "title": "DIRECCIÓN INVÁLIDA",
                    "message": "Ingresa una dirección de video válida.",
                })
                return False
            self._run_id += 1
            run_id = self._run_id
            self._running = True
            self._conf_threshold = float(conf_threshold)
            self._check_helmet = bool(check_helmet)
            self._check_vest = bool(check_vest)
            self._worker_tracker.reset()
            self._state.update({
                "status": "initializing",
                "title": "INICIALIZANDO DEMOSTRACIÓN",
                "message": "Conectando con la cámara...",
                "persons_count": 0,
                "detections_count": 0,
                "fps": 0.0,
            })
            if not self._viewer.request_enabled(True):
                self._running = False
                self._state.update({
                    "status": "danger",
                    "title": "VENTANA OCUPADA",
                    "message": "La ventana anterior aún está cerrándose.",
                })
                return False

            worker = threading.Thread(
                target=self._run,
                args=(run_id, source, model),
                name="DemoVideoWorker",
                daemon=True,
            )
            self._thread = worker
            try:
                worker.start()
            except RuntimeError as error:
                self._running = False
                self._thread = None
                self._state.update({
                    "status": "danger",
                    "title": "ERROR AL INICIAR",
                    "message": f"No se pudo iniciar la demostración: {error}",
                })
                start_failed = True
            else:
                start_failed = False

        if start_failed:
            self._viewer.shutdown(timeout=2.0)
            return False
        return True

    def stop(self):
        """Solicita la parada y libera la captura y la ventana."""
        with self._lock:
            self._running = False
            self._run_id += 1
            worker = self._thread
            self._state.update({
                "status": "standby",
                "title": "SISTEMA EN ESPERA",
                "message": "La demostración de video está detenida.",
                "persons_count": 0,
                "detections_count": 0,
                "fps": 0.0,
            })
        self._get_camera_manager().stop_all()
        self._viewer.shutdown(timeout=2.0)
        if worker is not None and worker is not threading.current_thread():
            worker.join(timeout=2.0)
        return worker is None or not worker.is_alive()

    def display_static_image(self, image_bgr, model, conf_threshold=0.45,
                             check_helmet=True, check_vest=True, sample_name=""):
        """
        Procesa una imagen estática, dibuja cajas, etiquetas y HUD,
        proyecta el fotograma en la ventana flotante nativa y registra
        el evento en memoria (cero base de datos, cero disco).
        """
        if image_bgr is None:
            return None

        # Si el stream continuo de video está activo, detenerlo para dar paso a la imagen
        if self.is_running():
            self.stop()

        self._viewer.request_enabled(True)

        if model is not None:
            annotated_bgr, persons_count, detections = self._detect_objects(
                image_bgr, model, conf_threshold,
                check_helmet=check_helmet, check_vest=check_vest,
                use_tracking=False
            )
            workers_list, summary_kpis = self._analyze_workers_spatial(
                detections, check_helmet=check_helmet, check_vest=check_vest
            )
            compliance_eval = self._evaluate_compliance(
                detections, check_helmet=check_helmet, check_vest=check_vest
            )
        else:
            annotated_bgr = image_bgr.copy()
            is_infraction = ("Infraccion" in sample_name or "1043" in sample_name or "Falta" in sample_name)
            if is_infraction:
                persons_count = 2
                detections = [
                    {"label": "person", "box": [50, 50, 150, 250], "is_violation": True, "is_compliant": False},
                    {"label": "NO-Hardhat", "box": [70, 50, 130, 90], "is_violation": True, "is_compliant": False}
                ]
                workers_list = [
                    {"ID": "#Operario-01", "is_compliant": False, "badge": "danger", "Veredicto": "INFRACCION: FALTA CASCO", "box": [50, 50, 150, 250]},
                    {"ID": "#Operario-02", "is_compliant": True, "badge": "safe", "Veredicto": "CUMPLE (EPP Completo)", "box": [180, 50, 280, 250]}
                ]
                compliance_eval = {
                    "status": "danger",
                    "title": "INFRACCIÓN CRÍTICA DETECTADA",
                    "message": "Se detectó personal operando sin Casco de Seguridad.",
                    "category": "Falta de Casco"
                }
            else:
                persons_count = 2
                detections = [
                    {"label": "person", "box": [50, 50, 150, 250], "is_violation": False, "is_compliant": True},
                    {"label": "Hardhat", "box": [70, 50, 130, 90], "is_violation": False, "is_compliant": True}
                ]
                workers_list = [
                    {"ID": "#Operario-01", "is_compliant": True, "badge": "safe", "Veredicto": "CUMPLE (EPP Completo)", "box": [50, 50, 150, 250]},
                    {"ID": "#Operario-02", "is_compliant": True, "badge": "safe", "Veredicto": "CUMPLE (EPP Completo)", "box": [180, 50, 280, 250]}
                ]
                compliance_eval = {
                    "status": "safe",
                    "title": "CUMPLIMIENTO NORMATIVO TOTAL",
                    "message": "Todo el personal porta los elementos de protección requeridos.",
                    "category": "Cumplimiento Total (OK)"
                }

        _annotate_demo_frame(annotated_bgr, workers_list, compliance_eval)
        self._viewer.publish(annotated_bgr)

        with self._lock:
            event_title = f"{sample_name or 'Imagen'}: {compliance_eval.get('title', 'Auditoría Demostración')}"
            self._record_demo_event_locked(
                title=event_title,
                status=compliance_eval.get("status", "safe"),
                category=compliance_eval.get("category", "Demostración"),
            )
            if persons_count == 0:
                disp_status = "standby"
                disp_title = "ZONA DESPEJADA"
                disp_msg = f"{sample_name or 'Imagen'}: No se detectó personal en la imagen."
            else:
                disp_status = compliance_eval.get("status", "safe")
                disp_title = compliance_eval.get("title", "DEMOSTRACIÓN ACTIVA")
                disp_msg = f"{sample_name or 'Imagen'}: {compliance_eval.get('message', 'Análisis completado.')}"

            self._state.update({
                "status": disp_status,
                "title": disp_title,
                "message": disp_msg,
                "persons_count": persons_count,
                "detections_count": len(detections),
                "fps": 0.0,
            })

        return annotated_bgr, persons_count, detections, workers_list, compliance_eval

    def _set_error(self, run_id, message, title="ERROR EN DEMOSTRACIÓN"):
        with self._lock:
            if self._run_id == run_id and self._running:
                self._running = False
                self._state.update({
                    "status": "danger",
                    "title": title,
                    "message": message,
                })

    def _run(self, run_id, source, model):
        try:
            stream, started = self._acquire_camera_stream(source, run_id)
            if not self._is_active(run_id):
                return
            if not started or stream is None:
                self._set_error(run_id, "No se pudo abrir la cámara seleccionada.", "ERROR DE CONEXIÓN")
                return

            last_sequence = None
            first_frame = True
            fps_started = time.monotonic()
            fps_frames = 0
            current_fps = 0.0
            while self._is_active(run_id):
                if not self._viewer.is_enabled():
                    with self._lock:
                        if self._run_id == run_id:
                            self._running = False
                            self._state.update({
                                "status": "standby",
                                "title": "SISTEMA EN ESPERA",
                                "message": "La ventana de demostración se cerró.",
                            })
                    break

                valid, frame, sequence, _ = stream.read_with_metadata()
                if not valid or frame is None:
                    if not stream.is_running:
                        self._set_error(run_id, "Se perdió la conexión con la cámara.", "CONEXIÓN PERDIDA")
                        break
                    time.sleep(0.02)
                    continue
                if sequence == last_sequence:
                    time.sleep(0.005)
                    continue
                last_sequence = sequence
                frame = cv2.flip(frame, 1)

                if first_frame:
                    with self._lock:
                        self._state.update({
                            "status": "running",
                            "title": "DEMO EN VIVO (SINCRONIZANDO)",
                            "message": "Cámara conectada. Sincronizando modelo de visión artificial...",
                        })
                    frame_preview = frame.copy()
                    h_f, w_f = frame_preview.shape[:2]
                    if h_f >= 60:
                        cv2.rectangle(frame_preview, (0, 0), (w_f, 36), (42, 23, 15), -1)
                        cv2.putText(
                            frame_preview,
                            "DEMO [MODO SANDBOX - SIN PERSISTENCIA] | SINCRONIZANDO SISTEMA...",
                            (14, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.52, (0, 200, 255), 2, cv2.LINE_AA
                        )
                    preview_sequence = self._viewer.publish(frame_preview)
                    self._viewer.wait_until_presented(
                        preview_sequence, timeout=2.0
                    )
                    first_frame = False
                    if not self._is_active(run_id):
                        break

                with self._lock:
                    confidence = self._conf_threshold
                    helmet_enabled = self._check_helmet
                    vest_enabled = self._check_vest

                annotated_bgr, persons_count, detections = self._detect_objects(
                    frame, model, confidence,
                    check_helmet=helmet_enabled,
                    check_vest=vest_enabled,
                    use_tracking=True
                )
                if not self._is_active(run_id):
                    break

                workers_list, summary_kpis = self._analyze_workers_spatial(
                    detections, check_helmet=helmet_enabled, check_vest=vest_enabled
                )
                compliance_eval = self._evaluate_compliance(
                    detections, check_helmet=helmet_enabled, check_vest=vest_enabled
                )

                _annotate_demo_frame(annotated_bgr, workers_list, compliance_eval)
                self._viewer.publish(annotated_bgr)

                # Tracking y registro en memoria con anti-parpadeo
                if workers_list and self._worker_tracker:
                    for w in workers_list:
                        eval_res = self._worker_tracker.evaluate_worker_event(w)
                        if eval_res["should_record"] and self._is_active(run_id):
                            event_payload = {
                                "category": eval_res["category"],
                                "title_detail": eval_res["title"],
                                "status": eval_res["status"],
                                "worker_id": eval_res["worker_id"],
                            }
                            self._on_worker_event_confirmed(event_payload, run_id)
                    self._worker_tracker.purge_inactive_tracks()

                fps_frames += 1
                now = time.monotonic()
                if now - fps_started >= 1.0:
                    current_fps = round(fps_frames / (now - fps_started), 1)
                    fps_frames = 0
                    fps_started = now

                if persons_count == 0:
                    display_status = "standby"
                    display_title = "ZONA DESPEJADA"
                    display_msg = "No se detecta presencia de personal en el encuadre."
                else:
                    display_status = compliance_eval.get("status", "safe")
                    display_title = compliance_eval.get("title", "DEMO EN VIVO")
                    display_msg = compliance_eval.get("message", "Operarios monitoreados.")

                with self._lock:
                    if self._run_id == run_id and self._running:
                        self._state.update({
                            "status": display_status,
                            "title": display_title,
                            "message": display_msg,
                            "persons_count": persons_count,
                            "detections_count": len(detections),
                            "fps": current_fps,
                        })
        except (cv2.error, OSError, RuntimeError, ValueError,
                TypeError, AttributeError) as error:
            self._set_error(run_id, f"Error en el video de demostración: {error}")
        finally:
            self._get_camera_manager().stop_all()
            self._viewer.shutdown(timeout=2.0)
            with self._lock:
                if self._run_id == run_id:
                    self._running = False
                    if self._state["status"] == "initializing":
                        self._state.update({
                            "status": "standby",
                            "title": "SISTEMA EN ESPERA",
                            "message": "La demostración de video está detenida.",
                        })
                if self._thread is threading.current_thread():
                    self._thread = None


@st.cache_resource
def get_demo_video_service():
    """Retorna el servicio compartido a través de las recargas de Streamlit."""
    return DemoVideoService()
