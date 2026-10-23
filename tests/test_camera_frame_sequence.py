"""Pruebas simuladas de la secuencia de captura de ThreadedCamera."""

import importlib.util
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np


camera_path = Path(__file__).resolve().parents[1] / "modules" / "camera.py"
spec = importlib.util.spec_from_file_location("camera_module_under_test", camera_path)
camera_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(camera_module)


class _FakeCapture:
    def __init__(self, *args):
        self.opened = True
        self.count = 0
        self.lock = threading.Lock()

    def isOpened(self):
        return self.opened

    def set(self, *_args):
        return True

    def read(self):
        with self.lock:
            if not self.opened:
                return False, None
            self.count += 1
            return True, np.full((8, 12, 3), self.count % 255, dtype=np.uint8)

    def release(self):
        self.opened = False


class ThreadedCameraSequenceTests(unittest.TestCase):
    def test_metadata_advances_and_legacy_read_shape_is_preserved(self):
        with patch.object(camera_module.cv2, "VideoCapture", side_effect=_FakeCapture):
            camera = camera_module.ThreadedCamera(source=0, width=12, height=8)
            self.assertTrue(camera.start())
            self.assertTrue(self._wait_for(lambda: camera.read_with_metadata()[2] >= 2))

            ok, frame = camera.read()
            self.assertTrue(ok)
            self.assertEqual(frame.shape, (8, 12, 3))

            ok, frame, sequence, captured_at = camera.read_with_metadata()
            self.assertTrue(ok)
            self.assertGreaterEqual(sequence, 2)
            self.assertGreater(captured_at, 0.0)
            self.assertLessEqual(captured_at, time.monotonic())

            camera.stop()
            self.assertFalse(camera.thread.is_alive())
            self.assertEqual(camera.read(), (False, None))

            self.assertTrue(camera.start())
            self.assertTrue(self._wait_for(
                lambda: camera.read_with_metadata()[2] > sequence
            ))
            restarted_sequence = camera.read_with_metadata()[2]
            self.assertGreater(restarted_sequence, sequence)
            camera.stop()

    def test_manager_retains_blocked_reader_until_it_finishes(self):
        entered = threading.Event()
        release = threading.Event()
        captures = []

        class BlockingCapture(_FakeCapture):
            def __init__(self, *args):
                super().__init__(*args)
                self.block_read = len(captures) == 0
                captures.append(self)

            def read(self):
                if self.block_read:
                    entered.set()
                    release.wait(5.0)
                return super().read()

        manager = camera_module.CameraStreamManager()
        with patch.object(camera_module.cv2, "VideoCapture", side_effect=BlockingCapture):
            stream = manager.get_stream(source=0, width=12, height=8)
            self.assertTrue(stream.start())
            self.assertTrue(entered.wait(1.0))
            blocked_reader = stream.thread

            manager.stop_all()
            self.assertTrue(blocked_reader.is_alive())
            self.assertIs(manager.current_stream, stream)

            pending_stream = manager.get_stream(source=0, width=12, height=8)
            self.assertIs(pending_stream, stream)
            self.assertFalse(pending_stream.start())
            self.assertEqual(len(captures), 1)

            release.set()
            self.assertTrue(self._wait_for(lambda: not blocked_reader.is_alive()))
            next_stream = manager.get_stream(source=0, width=12, height=8)
            self.assertIsNot(next_stream, stream)
            self.assertTrue(next_stream.start())
            self.assertEqual(len(captures), 2)
            manager.stop_all()

    @staticmethod
    def _wait_for(predicate, timeout=2.0):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            if predicate():
                return True
            time.sleep(0.005)
        return predicate()


if __name__ == "__main__":
    unittest.main()
