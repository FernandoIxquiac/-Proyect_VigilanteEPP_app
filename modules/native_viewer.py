"""Visor OpenCV con un único hilo propietario de la ventana."""

import threading
import time

import cv2


class LatestFrameNativeViewer:
    """Gestiona una ventana nativa usando únicamente el cuadro más reciente."""

    def __init__(self, window_name, cv_module=None):
        self._window_name = window_name
        self._cv = cv_module or cv2
        self._condition = threading.Condition()
        self._enabled = False
        self._shutdown_requested = False
        self._window_created = False
        self._latest_frame = None
        self._latest_sequence = 0
        self._presented_sequence = 0
        self._last_error = None
        self._thread = None

    def request_enabled(self, enabled):
        """Envía una solicitud de apertura o cierre sin tocar OpenCV en este hilo."""
        enabled = bool(enabled)
        worker_to_join = None
        with self._condition:
            self._enabled = enabled
            if not enabled:
                self._condition.notify_all()
                return True

            if self._thread is not None and self._thread.is_alive():
                if self._shutdown_requested:
                    worker_to_join = self._thread
                else:
                    self._last_error = None
                    self._condition.notify_all()
                    return True

        if worker_to_join is not None:
            worker_to_join.join(timeout=2.0)
            if worker_to_join.is_alive():
                return False

        with self._condition:
            self._enabled = True
            self._shutdown_requested = False
            self._last_error = None
            if self._thread is None or not self._thread.is_alive():
                self._thread = threading.Thread(
                    target=self._owner_loop,
                    name="NativeViewerOwner",
                    daemon=True,
                )
                self._thread.start()
            self._condition.notify_all()
        return True

    def publish(self, frame_bgr):
        """Reemplaza el cuadro pendiente; nunca acumula una cola de video."""
        if frame_bgr is None:
            return None
        frame_copy = frame_bgr.copy()
        with self._condition:
            self._latest_frame = frame_copy
            self._latest_sequence += 1
            sequence = self._latest_sequence
            self._condition.notify_all()
            return sequence

    def wait_until_presented(self, sequence, timeout=1.0):
        """Espera opcional para asegurar la primera presentación antes de inferir."""
        if sequence is None:
            return False
        deadline = time.monotonic() + timeout
        with self._condition:
            while self._presented_sequence < sequence:
                if not self._enabled or self._last_error is not None:
                    return False
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return False
                self._condition.wait(remaining)
            return True

    def is_enabled(self):
        """Indica si la ventana sigue solicitada por el usuario."""
        with self._condition:
            return self._enabled

    def shutdown(self, timeout=2.0):
        """Solicita el cierre y espera a que el hilo propietario libere la ventana."""
        with self._condition:
            self._enabled = False
            self._shutdown_requested = True
            self._condition.notify_all()
            worker = self._thread

        if worker is not None and worker is not threading.current_thread():
            worker.join(timeout=timeout)
        return worker is None or not worker.is_alive()

    def _set_enabled_from_owner(self, enabled, error=None):
        with self._condition:
            self._enabled = enabled
            self._last_error = error
            self._condition.notify_all()

    def _create_window(self):
        self._cv.namedWindow(self._window_name, self._cv.WINDOW_NORMAL)
        with self._condition:
            self._window_created = True
            self._condition.notify_all()
        self._cv.resizeWindow(self._window_name, 1024, 576)

    def _destroy_window(self):
        with self._condition:
            window_created = self._window_created
        if window_created:
            try:
                self._cv.destroyWindow(self._window_name)
            except cv2.error:
                pass
            with self._condition:
                self._window_created = False
                self._condition.notify_all()

    def _owner_loop(self):
        try:
            self._owner_loop_body()
        except cv2.error as error:
            self._set_enabled_from_owner(False, str(error))
        finally:
            self._destroy_window()
            with self._condition:
                self._enabled = False
                self._shutdown_requested = False
                self._thread = None
                self._condition.notify_all()

    def _owner_loop_body(self):
        while True:
            with self._condition:
                if self._shutdown_requested:
                    return
                enabled = self._enabled
                window_created = self._window_created
                sequence = self._latest_sequence
                frame = self._latest_frame if sequence > self._presented_sequence else None

                if not enabled:
                    if not window_created:
                        self._condition.wait(timeout=0.05)
                        continue
                elif frame is None and not window_created:
                    self._condition.wait(timeout=0.05)
                    continue

            if not enabled:
                self._destroy_window()
                continue

            if not window_created:
                self._create_window()

            if frame is not None:
                self._cv.imshow(self._window_name, frame)
                with self._condition:
                    self._presented_sequence = max(self._presented_sequence, sequence)
                    self._condition.notify_all()
            elif self._cv is cv2 and self._latest_frame is not None and window_created:
                # Repintado continuo en OpenCV real para mantener el Device Context Win32 activo
                # y evitar que el compositor de Windows (DWM) deje el fondo gris durante warmup de inferencia.
                self._cv.imshow(self._window_name, self._latest_frame)

            wait_delay = 20 if (self._cv is cv2 and frame is None) else 1
            key = self._cv.waitKey(wait_delay) & 0xFF
            try:
                visible = self._cv.getWindowProperty(
                    self._window_name, self._cv.WND_PROP_VISIBLE
                )
            except cv2.error:
                visible = 0

            if key == 27 or visible < 1:
                self._set_enabled_from_owner(False)
                self._destroy_window()
            else:
                with self._condition:
                    if not self._shutdown_requested:
                        self._condition.wait(timeout=0.02)
