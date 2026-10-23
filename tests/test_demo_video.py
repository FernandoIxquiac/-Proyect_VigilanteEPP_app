"""Pruebas del video de demostración sin cámara ni base operativa."""

import threading
import time
import unittest
from unittest.mock import patch

import cv2
import numpy as np

import modules.demo_video as demo_module
from modules.camera_sources import CAMERA_OPTIONS, resolve_camera_source


def wait_for(predicate, timeout=2.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.005)
    return predicate()


class FakeStream:
    def __init__(self):
        self.frame = np.full((24, 32, 3), 64, dtype=np.uint8)
        self.is_running = False
        self.thread = None
        self.sequence = 1
        self.start_result = True

    def start(self):
        self.is_running = self.start_result
        return self.start_result

    def read_with_metadata(self):
        if not self.is_running:
            return False, None, self.sequence, time.monotonic()
        return True, self.frame.copy(), self.sequence, time.monotonic()

    def stop(self):
        self.is_running = False


class FakeManager:
    def __init__(self):
        self.stream = FakeStream()
        self.sources = []
        self.stop_calls = 0

    def get_stream(self, source):
        self.sources.append(source)
        return self.stream

    def stop_all(self):
        self.stop_calls += 1
        self.stream.stop()


class FakeViewer:
    def __init__(self, window_name):
        self.enabled = False
        self.frames = []

    def request_enabled(self, enabled):
        self.enabled = enabled
        return True

    def publish(self, frame):
        self.frames.append(frame.copy())
        return len(self.frames)

    def wait_until_presented(self, sequence, timeout=1.0):
        return True

    def is_enabled(self):
        return self.enabled

    def shutdown(self, timeout=2.0):
        self.enabled = False
        return True


class DemoVideoTests(unittest.TestCase):
    def setUp(self):
        self.manager = FakeManager()
        camera_patch = patch.object(
            demo_module, "get_camera_manager", return_value=self.manager
        )
        viewer_patch = patch.object(
            demo_module, "LatestFrameNativeViewer", FakeViewer
        )
        camera_patch.start()
        viewer_patch.start()
        self.addCleanup(camera_patch.stop)
        self.addCleanup(viewer_patch.stop)

    def test_sources_are_shared_with_live_mode(self):
        self.assertEqual(resolve_camera_source(CAMERA_OPTIONS[1])[0], 1)
        self.assertEqual(resolve_camera_source(CAMERA_OPTIONS[2])[0], 2)
        self.assertEqual(
            resolve_camera_source(CAMERA_OPTIONS[3], " rtsp://camera/video "),
            ("rtsp://camera/video", "Flujo IP"),
        )

    def test_video_marks_are_shown_only_in_native_window(self):
        def detect(frame, model, conf_threshold, **options):
            self.assertTrue(options["use_tracking"])
            annotated = frame.copy()
            annotated[0, 0] = (0, 0, 255)
            return annotated, 1, [{"label": "Persona"}]

        with patch.object(demo_module, "detect_objects", side_effect=detect):
            with patch.object(demo_module.cv2, "imencode") as encode_mock:
                with patch("sqlite3.connect") as database_connect:
                    with patch.object(demo_module.cv2, "imwrite") as save_mock:
                        service = demo_module.DemoVideoService()
                        self.assertTrue(service.start(source=1, model=object()))
                        self.assertTrue(wait_for(
                            lambda: service.is_running() and len(service._viewer.frames) >= 2
                        ))
                        state = service.get_state()
                        self.assertEqual(state["persons_count"], 1)
                        self.assertEqual(state["detections_count"], 1)
                        self.assertIn("recent_events", state)
                        self.assertIn("total_inspections", state)
                        self.assertIn("compliance_pct", state)
                        self.assertIn("infractions_count", state)
                        self.assertIn("title", state)
                        self.assertEqual(self.manager.sources, [1])
                        self.assertGreaterEqual(len(service._viewer.frames), 2)
                        np.testing.assert_array_equal(
                            service._viewer.frames[-1][0, 0], (0, 0, 255)
                        )
                        self.assertTrue(service.stop())
                        self.assertFalse(service.is_busy())
                        database_connect.assert_not_called()
                        save_mock.assert_not_called()
                encode_mock.assert_not_called()
        self.assertGreaterEqual(self.manager.stop_calls, 1)

    def test_stop_during_inference_drops_late_result(self):
        entered = threading.Event()
        release = threading.Event()

        def detect(frame, model, conf_threshold, **options):
            entered.set()
            release.wait(2.0)
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), 1, []

        with patch.object(demo_module, "detect_objects", side_effect=detect):
            service = demo_module.DemoVideoService()
            self.assertTrue(service.start(source=0, model=object()))
            self.assertTrue(entered.wait(1.0))
            stop_thread = threading.Thread(target=service.stop)
            stop_thread.start()
            self.assertTrue(wait_for(lambda: not service.is_running()))
            release.set()
            stop_thread.join(timeout=2.0)
            self.assertFalse(stop_thread.is_alive())
            self.assertEqual(len(service._viewer.frames), 1)
            self.assertEqual(service.get_state()["status"], "standby")

    def test_settings_apply_to_next_video_frame(self):
        observed = []

        def detect(frame, model, confidence, **options):
            observed.append((confidence, options["check_helmet"],
                             options["check_vest"]))
            return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), 0, []

        with patch.object(demo_module, "detect_objects", side_effect=detect):
            service = demo_module.DemoVideoService()
            self.assertTrue(service.start(source=0, model=object()))
            self.assertTrue(wait_for(lambda: len(observed) == 1))
            service.update_config(0.30, False, True)
            self.manager.stream.sequence = 2
            self.assertTrue(wait_for(lambda: len(observed) == 2))
            service.stop()
        self.assertEqual(observed[0], (0.45, True, True))
        self.assertEqual(observed[1], (0.30, False, True))

    def test_missing_model_cannot_open_camera(self):
        service = demo_module.DemoVideoService()
        self.assertFalse(service.start(source=0, model=None))
        self.assertFalse(self.manager.sources)
        self.assertEqual(service.get_state()["status"], "danger")

    def test_camera_failure_does_not_block_a_later_start(self):
        service = demo_module.DemoVideoService()
        self.manager.stream.start_result = False
        self.assertTrue(service.start(source=2, model=object()))
        self.assertTrue(wait_for(
            lambda: service.get_state()["status"] == "danger"
        ))
        self.assertTrue(wait_for(lambda: not service.is_busy()))
        self.manager.stream.start_result = True
        with patch.object(demo_module, "detect_objects", return_value=(
            np.zeros((24, 32, 3), dtype=np.uint8), 0, []
        )):
            self.assertTrue(service.start(source=2, model=object()))
            self.assertTrue(wait_for(
                lambda: service.is_running()
            ))
            service.stop()

    def test_closing_native_window_releases_camera(self):
        with patch.object(demo_module, "detect_objects", return_value=(
            np.zeros((24, 32, 3), dtype=np.uint8), 0, []
        )):
            service = demo_module.DemoVideoService()
            self.assertTrue(service.start(source=0, model=object()))
            self.assertTrue(wait_for(
                lambda: service.is_running()
            ))
            service._viewer.enabled = False
            self.assertTrue(wait_for(lambda: not service.is_busy()))
        self.assertEqual(service.get_state()["status"], "standby")
        self.assertGreaterEqual(self.manager.stop_calls, 1)

    def test_display_static_image_zero_persistence(self):
        sample_img = np.full((100, 100, 3), 128, dtype=np.uint8)
        service = demo_module.DemoVideoService()

        with patch("sqlite3.connect") as database_connect:
            with patch.object(demo_module.cv2, "imwrite") as save_mock:
                res = service.display_static_image(
                    sample_img, model=None, sample_name="Caso 1042: Obrero con EPP Completo"
                )
                self.assertIsNotNone(res)
                state = service.get_state()
                self.assertEqual(state["total_inspections"], 1)
                self.assertEqual(state["compliance_pct"], 100.0)
                self.assertEqual(state["infractions_count"], 0)
                self.assertEqual(len(state["recent_events"]), 1)
                self.assertGreaterEqual(len(service._viewer.frames), 1)

                database_connect.assert_not_called()
                save_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
