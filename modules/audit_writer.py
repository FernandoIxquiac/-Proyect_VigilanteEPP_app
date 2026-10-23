"""Escritor acotado y único para eventos confirmados de auditoría."""

import sqlite3
import threading
from collections import deque

import cv2


class AuditEventWriter:
    """Persiste eventos en un hilo y limita cantidad y memoria de evidencias."""

    def __init__(self, write_event, on_result=None, max_pending_events=24,
                 max_pending_bytes=64 * 1024 * 1024):
        self._write_event = write_event
        self._on_result = on_result
        self._max_pending_events = int(max_pending_events)
        self._max_pending_bytes = int(max_pending_bytes)
        self._condition = threading.Condition()
        self._queue = deque()
        self._pending_events = 0
        self._pending_bytes = 0
        self._persisted_events = 0
        self._failed_events = 0
        self._rejected_events = 0
        self._last_error = None
        self._accepting = False
        self._thread = None

    def start(self):
        """Inicia el trabajador único de escritura."""
        with self._condition:
            if self._thread is not None and self._thread.is_alive():
                return
            self._accepting = True
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()

    def submit(self, event):
        """Encola una copia del evento y de la evidencia necesaria."""
        payload = dict(event)
        session_id = payload.get("session_id")
        if session_id is None:
            return self._reject("Evento sin session_id; no se encoló.")

        frame = payload.get("frame_bgr")
        keep_evidence = payload.get("status") in ("danger", "warning")
        evidence_bytes = int(getattr(frame, "nbytes", 0)) if keep_evidence else 0
        if evidence_bytes > self._max_pending_bytes:
            return self._reject(
                f"Evidencia excede el límite de {self._max_pending_bytes} bytes."
            )

        with self._condition:
            if not self._accepting:
                return self._reject_locked("El escritor está cerrado.")
            if self._pending_events >= self._max_pending_events:
                return self._reject_locked("Cola de auditoría llena por cantidad.")
            if self._pending_bytes + evidence_bytes > self._max_pending_bytes:
                return self._reject_locked("Cola de auditoría llena por memoria.")
            try:
                payload["frame_bgr"] = frame.copy() if keep_evidence and frame is not None else None
            except (AttributeError, MemoryError, ValueError) as exc:
                return self._reject_locked(
                    f"No se pudo copiar la evidencia: {exc.__class__.__name__}."
                )
            self._queue.append((payload, evidence_bytes))
            self._pending_events += 1
            self._pending_bytes += evidence_bytes
            self._condition.notify()
            return True, None

    def close(self, timeout=5.0):
        """Deja de aceptar eventos y espera el drenado de la cola."""
        with self._condition:
            self._accepting = False
            self._condition.notify_all()
            thread = self._thread
        if thread is not None and thread is not threading.current_thread():
            thread.join(timeout=max(0.0, float(timeout)))
        return self.is_drained()

    def is_drained(self):
        with self._condition:
            thread_finished = self._thread is None or not self._thread.is_alive()
            return self._pending_events == 0 and thread_finished

    def get_status(self):
        with self._condition:
            return {
                "pending_events": self._pending_events,
                "pending_bytes": self._pending_bytes,
                "persisted_events": self._persisted_events,
                "failed_events": self._failed_events,
                "rejected_events": self._rejected_events,
                "last_error": self._last_error,
                "accepting": self._accepting,
                "running": bool(self._thread and self._thread.is_alive()),
                "max_pending_events": self._max_pending_events,
                "max_pending_bytes": self._max_pending_bytes,
            }

    def _reject(self, message):
        with self._condition:
            return self._reject_locked(message)

    def _reject_locked(self, message):
        self._rejected_events += 1
        self._last_error = message
        return False, message

    def _run(self):
        while True:
            with self._condition:
                while not self._queue and self._accepting:
                    self._condition.wait()
                if not self._queue and not self._accepting:
                    return
                payload, evidence_bytes = self._queue.popleft()

            error = None
            event_id = None
            try:
                event_id = self._write_event(**payload)
                if event_id is None:
                    raise RuntimeError("La persistencia no devolvió un identificador de evento.")
            except (sqlite3.Error, OSError, ValueError, TypeError, RuntimeError, cv2.error) as exc:
                error = str(exc) or exc.__class__.__name__

            with self._condition:
                self._pending_events -= 1
                self._pending_bytes -= evidence_bytes
                if error is None:
                    self._persisted_events += 1
                else:
                    self._failed_events += 1
                    self._last_error = error
                self._condition.notify_all()

            if self._on_result is not None:
                self._on_result(payload, event_id, error)
