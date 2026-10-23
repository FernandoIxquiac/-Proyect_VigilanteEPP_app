"""Pruebas aisladas del primer cuadro del servicio de auditoría."""

import importlib
import sys
import threading
import time
import types
import unittest
from pathlib import Path
from unittest.mock import patch

import cv2
import numpy as np


# Sustituir dependencias con efectos operativos antes de importar el auditor.
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
modules_package = types.ModuleType("modules")
modules_package.__path__ = [str(root.joinpath("modules"))]
sys.modules["modules"] = modules_package
camera_stub = types.ModuleType("modules.camera")
database_stub = types.ModuleType("modules.database")
metrics_stub = types.ModuleType("modules.metrics")
detector_stub = types.ModuleType("modules.detector")
tracker_stub = types.ModuleType("modules.tracker_manager")
camera_stub = types.ModuleType("modules.camera")
database_stub = types.ModuleType("modules.database")
metrics_stub = types.ModuleType("modules.metrics")
detector_stub = types.ModuleType("modules.detector")
tracker_stub = types.ModuleType("modules.tracker_manager")


class _FakeCameraManager:
    def __init__(self, frame):
        self.stream = _FakeCameraStream(frame)

    def get_stream(self, source):
        return self.stream

    def stop_all(self):
        self.stream.stopped = True


class _FakeCameraStream:
    def __init__(self, frame):
        self.frame = frame
        self.reads = 0
        self.stopped = False
        self.start_gate = None
        self.start_result = True
        self.start_entered = threading.Event()
        self.start_finished = threading.Event()
        self.sequence = 0
        self.captured_at = 0.0
        self.repeat_latest = False
        self.is_running = False

    def start(self):
        self.reads = 0
        self.stopped = False
        self.is_running = self.start_result
        self.start_entered.set()
        if self.start_gate is not None:
            self.start_gate.wait(3.0)
        self.start_finished.set()
        return self.start_result

    def stop(self):
        self.stopped = True
        self.is_running = False

    def read(self):
        self.reads += 1
        if self.stopped or not self.is_running:
            return False, None
        if self.reads == 1 or self.repeat_latest:
            if self.reads == 1:
                self.sequence += 1
                self.captured_at = time.monotonic()
            return True, self.frame.copy()
        return False, None

    def read_with_metadata(self):
        ret, frame = self.read()
        return ret, frame, self.sequence, self.captured_at


camera_stub.get_camera_manager = lambda: None
database_stub.start_camera_session = lambda: "test-session"
database_stub.end_camera_session = lambda *args: None
metrics_stub.record_camera_audit = lambda **kwargs: None
detector_stub.detect_objects = lambda frame, *args, **kwargs: (
    cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) if frame is not None else np.zeros((24, 32, 3), dtype=np.uint8),
    0,
    []
)
detector_stub.analyze_workers_spatial = lambda *args, **kwargs: (
    [],
    {"total": 0, "compliant": 0, "infractions": 0, "rate": 100.0}
)
detector_stub.evaluate_compliance = lambda *args, **kwargs: {
    "status": "standby",
    "title": "ZONA DESPEJADA",
    "message": "No hay personal",
    "category": None,
    "has_violation": False,
}


class _FakeTracker:
    def __init__(self, **kwargs):
        pass

    def reset(self):
        pass

    def purge_inactive_tracks(self):
        pass

    def evaluate_worker_event(self, worker_dict):
        return {
            "should_record": False,
            "reason": "suppressed",
            "category": "Cumplimiento Total (OK)",
            "title": f"{worker_dict.get('ID', '#Operario-01')}: EPP Completo Verificado",
            "status": "safe",
            "worker_id": worker_dict.get("ID", "#Operario-01"),
        }


tracker_stub.WorkerTrackManager = _FakeTracker
sys.modules.update({
    "modules.camera": camera_stub,
    "modules.database": database_stub,
    "modules.metrics": metrics_stub,
    "modules.detector": detector_stub,
    "modules.tracker_manager": tracker_stub,
})
auditor_module = importlib.import_module("modules.auditor")
native_viewer_module = importlib.import_module("modules.native_viewer")


def _detector_result(frame, model, conf_threshold, **kwargs):
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), 0, []


def _wait_for(predicate, timeout=2.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.005)
    return predicate()


class AuditorFirstFrameTests(unittest.TestCase):
    def setUp(self):
        self.frame = np.full((24, 32, 3), 64, dtype=np.uint8)
        self.camera_manager = _FakeCameraManager(self.frame)
        self.persist = patch.object(auditor_module, "record_camera_audit")
        self.persist_mock = self.persist.start()
        self.addCleanup(self.persist.stop)
        self.manager = patch.object(
            auditor_module, "get_camera_manager", return_value=self.camera_manager
        )
        self.manager.start()
        self.addCleanup(self.manager.stop)
        self.analyze = patch.object(
            auditor_module, "analyze_workers_spatial", return_value=([], {})
        )
        self.analyze.start()
        self.addCleanup(self.analyze.stop)
        self.compliance = patch.object(
            auditor_module,
            "evaluate_compliance",
            return_value={"status": "standby", "title": "ZONA DESPEJADA"},
        )
        self.compliance.start()
        self.addCleanup(self.compliance.stop)

    def _start(self, detector, native=False, source=0):
        detector_patch = patch.object(auditor_module, "detect_objects", side_effect=detector)
        detector_patch.start()
        self.addCleanup(detector_patch.stop)
        service = auditor_module.LiveAuditorService()
        service.start(source=source, model=object(), show_native_window=native)
        return service

    def test_same_capture_sequence_is_inferred_only_once(self):
        calls = []
        detector_gate = threading.Event()

        def blocking_detector(frame, model, conf_threshold, **kwargs):
            calls.append(frame.copy())
            detector_gate.wait(1.0)
            return _detector_result(frame, model, conf_threshold, **kwargs)

        service = self._start(blocking_detector)
        self.camera_manager.stream.repeat_latest = True
        self.assertTrue(_wait_for(lambda: len(calls) == 1))
        time.sleep(0.1)
        self.assertEqual(len(calls), 1)
        detector_gate.set()
        service.stop()

    def test_stop_during_inference_rejects_late_result_and_blocks_overlap(self):
        release = threading.Event()
        entered = threading.Event()

        def blocking_detector(frame, model, conf_threshold, **kwargs):
            entered.set()
            release.wait(3.0)
            return _detector_result(frame, model, conf_threshold, **kwargs)

        service = self._start(blocking_detector)
        self.assertTrue(entered.wait(1.0))
        old_thread = service._thread
        service.stop()
        self.assertFalse(service.is_running())
        self.assertEqual(service.get_latest_state()["status"], "standby")
        self.assertFalse(service.start(model=object()))
        release.set()
        self.assertTrue(_wait_for(lambda: not old_thread.is_alive()))
        self.assertEqual(service.get_latest_state()["status"], "standby")
        previous_frame_id = service.get_latest_state()["frame_id"]

        with patch.object(auditor_module, "detect_objects", side_effect=_detector_result):
            self.assertTrue(service.start(model=object()))
            self.assertTrue(_wait_for(
                lambda: service.get_latest_state().get("status") == "standby"
                and service.get_latest_state().get("frame_id", 0) > previous_frame_id
            ))
            fresh_state = service.get_latest_state()
            self.assertIsNone(fresh_state["frame_bytes"])
            self.assertGreater(fresh_state["capture_sequence"], 0)
            self.assertGreaterEqual(fresh_state["processed_at"], fresh_state["processing_started_at"])
            service.stop()

    def test_camera_disconnect_clears_last_published_image_and_result(self):
        service = self._start(_detector_result)
        self.assertTrue(_wait_for(
            lambda: service.get_latest_state().get("title") == "ZONA DESPEJADA"
            and service.get_latest_state().get("processed_at", 0) > 0
        ))
        stream = self.camera_manager.stream
        stream.is_running = False
        self.assertTrue(_wait_for(
            lambda: service.get_latest_state().get("title") == "CONEXIÓN DE CÁMARA PERDIDA"
        ))
        state = service.get_latest_state()
        self.assertFalse(state["is_running"])
        self.assertIsNone(state["frame_rgb"])
        self.assertIsNone(state["frame_bytes"])
        self.assertEqual(state["persons_count"], 0)

    def test_first_preview_is_published_before_blocked_detector(self):
        entered = threading.Event()
        release = threading.Event()

        def blocking_detector(*args, **kwargs):
            entered.set()
            release.wait(2.0)
            return _detector_result(*args, **kwargs)

        service = self._start(blocking_detector)
        self.assertTrue(entered.wait(1.0))
        state = service.get_latest_state()
        self.assertIsNone(state["frame_rgb"])
        self.assertIsNone(state["frame_bytes"])
        self.assertGreater(state["frame_id"], 0)
        self.assertEqual(state["status"], "initializing")
        self.assertNotEqual(state["status"], "safe")
        self.assertGreater(state["timestamp"], 1_000_000_000)
        self.assertEqual(state["persons_count"], 0)
        self.persist_mock.assert_not_called()
        release.set()
        service.stop()

    def test_native_only_pipeline_does_not_encode_browser_frames(self):
        with patch.object(auditor_module.cv2, "imencode") as encode_mock:
            service = self._start(_detector_result)
            self.assertTrue(_wait_for(
                lambda: service.get_latest_state()["title"] == "ZONA DESPEJADA"
            ))
            state = service.get_latest_state()
            self.assertIsNone(state["frame_rgb"])
            self.assertIsNone(state["frame_bytes"])
            self.assertGreater(state["timestamp"], 1_000_000_000)
            service.stop()
            encode_mock.assert_not_called()

    def test_stop_during_initialization_does_not_republish_activity(self):
        entered = threading.Event()
        release = threading.Event()

        def blocking_detector(*args, **kwargs):
            entered.set()
            release.wait(2.0)
            return _detector_result(*args, **kwargs)

        service = self._start(blocking_detector)
        self.assertTrue(entered.wait(1.0))
        service.stop()
        release.set()
        self.assertTrue(_wait_for(lambda: service._thread is None))
        state = service.get_latest_state()
        self.assertFalse(state["is_running"])
        self.assertIsNone(state["frame_rgb"])
        self.assertIsNone(state["frame_bytes"])

    def test_stop_while_camera_start_is_blocked_preserves_standby(self):
        for start_result in (False, True):
            with self.subTest(start_result=start_result):
                release_start = threading.Event()
                stream = self.camera_manager.stream
                stream.start_entered = threading.Event()
                stream.start_finished = threading.Event()
                stream.start_gate = release_start
                stream.start_result = start_result

                service = auditor_module.LiveAuditorService()
                service.start(model=object())
                worker = service._thread
                self.assertTrue(stream.start_entered.wait(1.0))

                service.stop()
                release_start.set()
                worker.join(timeout=1.0)

                self.assertFalse(worker.is_alive())
                self.assertTrue(stream.start_finished.is_set())
                self.assertTrue(stream.stopped)
                state = service.get_latest_state()
                self.assertFalse(state["is_running"])
                self.assertEqual(state["status"], "standby")
                self.assertEqual(state["title"], "SISTEMA EN ESPERA")
                self.assertIsNone(state["frame_rgb"])
                self.assertIsNone(state["frame_bytes"])
                stream.start_gate = None
                stream.start_result = True

    def test_new_source_waits_for_previous_camera_reader_to_exit(self):
        previous_released = threading.Event()
        current_stream = _FakeCameraStream(self.frame)

        class ClosingStream:
            def __init__(self):
                self.thread = self
                self.attempts = 0

            def is_alive(self):
                return not previous_released.is_set()

            def start(self):
                self.attempts += 1
                return False

        class SwitchingManager:
            def __init__(self):
                self.closing_stream = ClosingStream()
                self.sources = []

            def get_stream(self, source):
                self.sources.append(source)
                return (
                    self.closing_stream
                    if not previous_released.is_set()
                    else current_stream
                )

            def stop_all(self):
                current_stream.stop()

        manager = SwitchingManager()
        with patch.object(auditor_module, "get_camera_manager", return_value=manager):
            service = self._start(_detector_result, source=1)
            self.assertTrue(_wait_for(lambda: manager.closing_stream.attempts > 0))
            self.assertNotEqual(service.get_latest_state()["status"], "danger")
            previous_released.set()
            self.assertTrue(_wait_for(
                lambda: service.get_latest_state()["title"] == "ZONA DESPEJADA"
            ))
            service.stop()
        self.assertTrue(all(source == 1 for source in manager.sources))
        self.assertGreaterEqual(len(manager.sources), 2)

    def test_native_preview_is_shown_before_detector(self):
        entered = threading.Event()
        release = threading.Event()
        window_closed = threading.Event()
        order = []

        def blocking_detector(*args, **kwargs):
            order.append("detector")
            entered.set()
            release.wait(2.0)
            return _detector_result(*args, **kwargs)

        def window_property(*args):
            return 0 if entered.is_set() else 1

        def destroy_window(*args):
            order.append("destroy")
            window_closed.set()

        window_patch = patch.multiple(
            auditor_module.cv2,
            namedWindow=lambda *args: order.append("window"),
            resizeWindow=lambda *args: None,
            imshow=lambda *args: order.append("imshow"),
            waitKey=lambda *args: -1,
            getWindowProperty=window_property,
            destroyWindow=destroy_window,
        )
        window_patch.start()
        self.addCleanup(window_patch.stop)
        service = self._start(blocking_detector, native=True)
        self.assertTrue(entered.wait(1.0))
        self.assertLess(order.index("imshow"), order.index("detector"))
        self.assertTrue(window_closed.wait(1.0))
        self.assertFalse(service._native_viewer.is_enabled())
        self.assertFalse(release.is_set())
        release.set()
        service.stop()


class _FakeNativeCV:
    WINDOW_NORMAL = 0
    WND_PROP_VISIBLE = 1

    def __init__(self):
        self.lock = threading.Lock()
        self.visible = False
        self.open_count = 0
        self.destroy_count = 0
        self.frames = []
        self.key = -1
        self.owner_ids = set()

    def _record_owner(self):
        with self.lock:
            self.owner_ids.add(threading.get_ident())

    def namedWindow(self, name, flags):
        self._record_owner()
        with self.lock:
            self.visible = True
            self.open_count += 1

    def resizeWindow(self, name, width, height):
        self._record_owner()

    def imshow(self, name, frame):
        self._record_owner()
        with self.lock:
            self.frames.append(frame.copy())

    def waitKey(self, delay):
        self._record_owner()
        with self.lock:
            key = self.key
            self.key = -1
            return key

    def getWindowProperty(self, name, prop):
        self._record_owner()
        with self.lock:
            return 1 if self.visible else 0

    def destroyWindow(self, name):
        self._record_owner()
        with self.lock:
            self.visible = False
            self.destroy_count += 1

    def send_key(self, key):
        with self.lock:
            self.key = key

    def close_window(self):
        with self.lock:
            self.visible = False


class NativeViewerOwnerTests(unittest.TestCase):
    def test_latest_frame_esc_window_close_and_reopen_use_one_owner(self):
        fake_cv = _FakeNativeCV()
        viewer = native_viewer_module.LatestFrameNativeViewer(
            "test-window", cv_module=fake_cv
        )
        first_seq = viewer.publish(np.full((4, 4, 3), 10, dtype=np.uint8))
        second_seq = viewer.publish(np.full((4, 4, 3), 20, dtype=np.uint8))
        last_seq = viewer.publish(np.full((4, 4, 3), 30, dtype=np.uint8))
        viewer.request_enabled(True)
        self.assertTrue(viewer.wait_until_presented(last_seq, timeout=1.0))
        self.assertGreater(last_seq, second_seq)
        self.assertGreater(second_seq, first_seq)
        self.assertEqual(len(fake_cv.frames), 1)
        self.assertTrue(np.all(fake_cv.frames[-1] == 30))

        fake_cv.send_key(27)
        self.assertTrue(_wait_for(lambda: not viewer.is_enabled()))
        self.assertEqual(fake_cv.destroy_count, 1)

        viewer.request_enabled(True)
        reopened_seq = viewer.publish(np.full((4, 4, 3), 40, dtype=np.uint8))
        self.assertTrue(viewer.wait_until_presented(reopened_seq, timeout=1.0))
        fake_cv.close_window()
        self.assertTrue(_wait_for(lambda: not viewer.is_enabled()))
        self.assertEqual(fake_cv.destroy_count, 2)

        viewer.request_enabled(True)
        final_seq = viewer.publish(np.full((4, 4, 3), 50, dtype=np.uint8))
        self.assertTrue(viewer.wait_until_presented(final_seq, timeout=1.0))
        self.assertTrue(viewer.shutdown(timeout=1.0))
        self.assertEqual(fake_cv.open_count, 3)
        self.assertEqual(fake_cv.destroy_count, 3)
        self.assertEqual(len(fake_cv.owner_ids), 1)


if __name__ == "__main__":
    unittest.main()
