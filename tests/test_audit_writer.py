"""Pruebas aisladas del escritor y su integración en auditoría en vivo."""

import importlib
import importlib.util
import sqlite3
import sys
import tempfile
import threading
import time
import unittest
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch

import numpy as np

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root.joinpath("tests")))
sys.path.insert(0, str(root))
import test_auditor_first_frame as fixture

from modules.audit_writer import AuditEventWriter

database_spec = importlib.util.spec_from_file_location(
    "epp_test_database", root / "modules" / "database.py"
)
database_module = importlib.util.module_from_spec(database_spec)
database_spec.loader.exec_module(database_module)

auditor_module = fixture.auditor_module


def _event(frame, session_id="session-test", status="danger"):
    return {
        "category": "Sin Casco",
        "title_detail": "Prueba de persistencia",
        "status": status,
        "personnel_count": 1,
        "confidence": 98.0,
        "frame_bgr": frame,
        "session_id": session_id,
        "worker_id": "worker-test",
    }


class AuditEventWriterTests(unittest.TestCase):
    def setUp(self):
        self.frame = np.full((4, 6, 3), 100, dtype=np.uint8)

    def test_capacity_limits_evidence_and_rejects_without_counting_as_saved(self):
        entered = threading.Event()
        release = threading.Event()
        saved = []

        def slow_write(**event):
            entered.set()
            release.wait(2.0)
            saved.append(event)
            return len(saved)

        writer = AuditEventWriter(
            slow_write, max_pending_events=2, max_pending_bytes=144
        )
        writer.start()
        self.assertEqual(writer.submit(_event(self.frame)), (True, None))
        self.assertTrue(entered.wait(1.0))
        self.assertEqual(writer.submit(_event(self.frame)), (True, None))
        accepted, error = writer.submit(_event(self.frame))
        self.assertFalse(accepted)
        self.assertIn("cantidad", error)
        status = writer.get_status()
        self.assertEqual(status["pending_events"], 2)
        self.assertEqual(status["pending_bytes"], 144)
        self.assertEqual(status["persisted_events"], 0)
        self.assertEqual(status["rejected_events"], 1)

        release.set()
        self.assertTrue(writer.close(timeout=1.0))
        status = writer.get_status()
        self.assertEqual(status["pending_events"], 0)
        self.assertEqual(status["pending_bytes"], 0)
        self.assertEqual(status["persisted_events"], 2)
        self.assertEqual(status["rejected_events"], 1)
        self.assertIsNot(saved[0]["frame_bgr"], self.frame)
        self.assertEqual(saved[0]["session_id"], "session-test")

    def test_persistence_error_is_explicit_and_not_counted_as_saved(self):
        def failed_write(**_event_data):
            raise OSError("disco temporal no disponible")

        writer = AuditEventWriter(failed_write)
        writer.start()
        self.assertEqual(writer.submit(_event(self.frame)), (True, None))
        self.assertTrue(writer.close(timeout=1.0))
        status = writer.get_status()
        self.assertEqual(status["persisted_events"], 0)
        self.assertEqual(status["failed_events"], 1)
        self.assertIn("disco temporal", status["last_error"])

    def test_evidence_byte_limit_is_enforced_independently_of_event_limit(self):
        entered = threading.Event()
        release = threading.Event()

        def slow_write(**_event_data):
            entered.set()
            release.wait(2.0)
            return 1

        writer = AuditEventWriter(
            slow_write, max_pending_events=5, max_pending_bytes=100
        )
        writer.start()
        self.assertEqual(writer.submit(_event(self.frame)), (True, None))
        self.assertTrue(entered.wait(1.0))
        accepted, error = writer.submit(_event(self.frame))
        self.assertFalse(accepted)
        self.assertIn("memoria", error)
        status = writer.get_status()
        self.assertEqual(status["pending_events"], 1)
        self.assertEqual(status["pending_bytes"], 72)
        self.assertEqual(status["rejected_events"], 1)
        release.set()
        self.assertTrue(writer.close(timeout=1.0))

    def test_close_timeout_reports_pending_then_drains_in_order(self):
        entered = threading.Event()
        release = threading.Event()
        saved_sessions = []

        def blocked_write(**event_data):
            entered.set()
            release.wait(2.0)
            saved_sessions.append(event_data["session_id"])
            return 10

        writer = AuditEventWriter(blocked_write)
        writer.start()
        writer.submit(_event(self.frame, session_id="turn-42"))
        self.assertTrue(entered.wait(1.0))
        self.assertFalse(writer.close(timeout=0.01))
        pending = writer.get_status()
        self.assertEqual(pending["pending_events"], 1)
        self.assertEqual(pending["persisted_events"], 0)
        release.set()
        self.assertTrue(writer.close(timeout=1.0))
        self.assertEqual(saved_sessions, ["turn-42"])
        self.assertEqual(writer.get_status()["persisted_events"], 1)

    def test_service_keeps_session_open_and_reports_pending_on_incomplete_drain(self):
        class PendingWriter:
            def close(self, timeout=5.0):
                return False

            def is_drained(self):
                return False

            def get_status(self):
                return {
                    "pending_events": 1,
                    "pending_bytes": 72,
                    "persisted_events": 0,
                    "failed_events": 0,
                    "rejected_events": 0,
                    "last_error": None,
                    "accepting": False,
                    "running": True,
                    "max_pending_events": 24,
                    "max_pending_bytes": 64 * 1024 * 1024,
                }

        service = auditor_module.LiveAuditorService()
        service._audit_writer = PendingWriter()
        service._session_id = "session-pending"
        end_session = patch.object(auditor_module, "end_camera_session")
        end_session_mock = end_session.start()
        self.addCleanup(end_session.stop)

        self.assertFalse(service.start(model=object()))
        service.stop()
        state = service.get_latest_state()
        self.assertEqual(service._session_id, "session-pending")
        self.assertEqual(state["persistence_pending_events"], 1)
        self.assertIn("1 evento(s) siguen pendientes", state["persistence_last_error"])
        end_session_mock.assert_not_called()

    def test_safe_event_does_not_copy_or_retain_evidence(self):
        received = []
        writer = AuditEventWriter(lambda **event_data: received.append(event_data) or 1)
        writer.start()
        self.assertEqual(writer.submit(_event(self.frame, status="safe")), (True, None))
        self.assertTrue(writer.close(timeout=1.0))
        self.assertIsNone(received[0]["frame_bgr"])

    def test_slow_persistence_does_not_block_live_frame_publication(self):
        frame = np.full((24, 32, 3), 64, dtype=np.uint8)
        stream = _LiveTestStream(frame)
        manager = _LiveTestManager(stream)
        worker = {"ID": "worker-1", "box": [1, 1, 10, 20], "is_compliant": False}
        written = []
        end_session = patch.object(auditor_module, "end_camera_session")
        end_session_mock = end_session.start()
        self.addCleanup(end_session.stop)

        def slow_write(**event_data):
            time.sleep(0.25)
            path = Path(self.temp_dir.name, f"event_{len(written):03d}.bin")
            path.write_bytes(event_data["frame_bgr"].tobytes())
            written.append((event_data["session_id"], event_data["worker_id"], path))
            return len(written)

        def bounded_writer(write_event, on_result=None):
            return AuditEventWriter(
                write_event,
                on_result=on_result,
                max_pending_events=4,
                max_pending_bytes=16 * 1024,
            )

        self.temp_dir = tempfile.TemporaryDirectory(prefix="epp-audit-writer-test-")
        self.addCleanup(self.temp_dir.cleanup)
        persistence = patch.object(auditor_module, "record_camera_audit", side_effect=slow_write)
        manager_patch = patch.object(auditor_module, "get_camera_manager", return_value=manager)
        session_patch = patch.object(auditor_module, "start_camera_session", return_value="session-live-test")
        writer_patch = patch.object(auditor_module, "AuditEventWriter", side_effect=bounded_writer)
        detector_patch = patch.object(
            auditor_module,
            "detect_objects",
            side_effect=lambda image, *_args, **_kwargs: (
                fixture.cv2.cvtColor(image, fixture.cv2.COLOR_BGR2RGB), 1, []
            ),
        )
        analyze_patch = patch.object(
            auditor_module,
            "analyze_workers_spatial",
            return_value=([worker], {"total": 1, "compliant": 0, "infractions": 1, "rate": 0.0}),
        )
        compliance_patch = patch.object(
            auditor_module,
            "evaluate_compliance",
            return_value={"status": "danger", "title": "FALTA EPP", "message": "Prueba"},
        )
        tracker_patch = patch.object(auditor_module, "WorkerTrackManager", _LiveTestTracker)
        patches = [persistence, manager_patch, session_patch, writer_patch,
                   detector_patch, analyze_patch, compliance_patch, tracker_patch]
        for active_patch in patches:
            active_patch.start()
            self.addCleanup(active_patch.stop)

        service = auditor_module.LiveAuditorService()
        self.assertTrue(service.start(model=object()))
        lags = []
        max_pending_bytes = 0
        deadline = time.monotonic() + 0.9
        last_frame_id = -1
        while time.monotonic() < deadline:
            state = service.get_latest_state()
            if (state.get("frame_id", -1) != last_frame_id
                    and state.get("status") != "initializing"
                    and state.get("processed_at", 0) > 0):
                last_frame_id = state["frame_id"]
                lags.append(state["processed_at"] - state["captured_at"])
            max_pending_bytes = max(
                max_pending_bytes, state.get("persistence_pending_bytes", 0)
            )
            time.sleep(0.002)
        saturated_state = service.get_latest_state()
        self.assertGreaterEqual(len(lags), 8)
        self.assertLess(sum(lags) / len(lags), 0.10)
        self.assertGreater(saturated_state["persistence_rejected_events"], 0)
        self.assertIn("Cola de auditoría llena", saturated_state["persistence_last_error"])
        self.assertLessEqual(max_pending_bytes, 16 * 1024)

        service.stop()
        final_state = service.get_latest_state()
        self.assertEqual(final_state["persistence_pending_events"], 0)
        self.assertGreater(final_state["persistence_persisted_events"], 0)
        self.assertEqual(len(written), final_state["persistence_persisted_events"])
        self.assertTrue(all(session == "session-live-test" for session, _, _ in written))
        self.assertTrue(all(worker_id == "worker-1" for _, worker_id, _ in written))
        self.assertTrue(all(
            path.is_file() and path.read_bytes() == frame.tobytes()
            for _, _, path in written
        ))
        end_session_mock.assert_called_once_with(
            "session-live-test", len(written), len(written)
        )


class CameraEventEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(prefix="epp-camera-event-test-")
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.database_path = self.root / "events.sqlite3"
        self.captures_dir = self.root / "captures"
        self.captures_dir.mkdir()
        with sqlite3.connect(self.database_path) as connection:
            connection.execute("""
                CREATE TABLE camera_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    worker_id TEXT,
                    timestamp TEXT NOT NULL,
                    category TEXT NOT NULL,
                    details TEXT,
                    status TEXT NOT NULL,
                    personnel_count INTEGER,
                    confidence REAL,
                    evidence_path TEXT
                )
            """)

        @contextmanager
        def temporary_connection():
            connection = sqlite3.connect(self.database_path)
            try:
                yield connection
            finally:
                connection.close()

        self.connection_patch = patch.object(
            database_module, "get_connection", temporary_connection
        )
        self.connection_patch.start()
        self.addCleanup(self.connection_patch.stop)
        self.capture_patch = patch.object(
            database_module, "CAPTURES_DIR", str(self.captures_dir)
        )
        self.capture_patch.start()
        self.addCleanup(self.capture_patch.stop)
        counters_patch = patch.object(database_module, "update_session_counters")
        counters_patch.start()
        self.addCleanup(counters_patch.stop)
        self.frame = np.full((8, 12, 3), 90, dtype=np.uint8)

    def _writer_event(self, **event_data):
        return database_module.log_camera_event(
            category=event_data["category"],
            details=event_data["title_detail"],
            status=event_data["status"],
            personnel_count=event_data["personnel_count"],
            confidence=event_data["confidence"],
            frame_bgr=event_data["frame_bgr"],
            session_id=event_data["session_id"],
            worker_id=event_data["worker_id"],
        )

    def test_failed_imwrite_is_reported_to_writer_without_event_or_success_count(self):
        with patch.object(database_module.cv2, "imwrite", return_value=False):
            writer = AuditEventWriter(self._writer_event)
            writer.start()
            self.assertEqual(
                writer.submit(_event(self.frame, session_id="session-17")),
                (True, None),
            )
            self.assertTrue(writer.close(timeout=1.0))

        status = writer.get_status()
        self.assertEqual(status["persisted_events"], 0)
        self.assertEqual(status["failed_events"], 1)
        self.assertIn("no pudo escribir la evidencia", status["last_error"])
        with sqlite3.connect(self.database_path) as connection:
            self.assertEqual(connection.execute(
                "SELECT COUNT(*) FROM camera_events"
            ).fetchone()[0], 0)
        self.assertEqual(list(self.captures_dir.iterdir()), [])

    def test_saved_evidence_and_event_share_session_and_path(self):
        def save_jpeg(path, _frame, _options):
            Path(path).write_bytes(b"jpeg evidence")
            return True

        with patch.object(database_module.cv2, "imwrite", side_effect=save_jpeg):
            event_id = self._writer_event(**_event(self.frame, session_id="session-23"))

        with sqlite3.connect(self.database_path) as connection:
            row = connection.execute(
                "SELECT id, session_id, evidence_path FROM camera_events"
            ).fetchone()
        self.assertEqual(row[0], event_id)
        self.assertEqual(row[1], "session-23")
        evidence_path = Path(row[2])
        self.assertTrue(evidence_path.is_file())
        self.assertEqual(evidence_path.read_bytes(), b"jpeg evidence")

    def test_insert_failure_removes_only_new_evidence_file(self):
        unrelated_file = self.captures_dir / "otra_evidencia.jpg"
        unrelated_file.write_bytes(b"no borrar")
        with sqlite3.connect(self.database_path) as connection:
            connection.execute("CREATE TRIGGER reject_camera_event BEFORE INSERT ON camera_events BEGIN SELECT RAISE(ABORT, 'test rejection'); END")

        def save_jpeg(path, _frame, _options):
            Path(path).write_bytes(b"temporary evidence")
            return True

        with patch.object(database_module.cv2, "imwrite", side_effect=save_jpeg):
            with self.assertRaises(sqlite3.IntegrityError):
                self._writer_event(**_event(self.frame, session_id="session-24"))
        self.assertEqual(list(self.captures_dir.iterdir()), [unrelated_file])
        self.assertEqual(unrelated_file.read_bytes(), b"no borrar")


class _LiveTestStream:
    def __init__(self, frame):
        self.frame = frame
        self.running = False
        self.sequence = 0

    def start(self):
        self.running = True
        return True

    def read_with_metadata(self):
        if not self.running:
            return False, None, self.sequence, 0.0
        self.sequence += 1
        return True, self.frame.copy(), self.sequence, time.monotonic()

    def stop(self):
        self.running = False


class _LiveTestManager:
    def __init__(self, stream):
        self.stream = stream

    def get_stream(self, _source):
        return self.stream

    def stop_all(self):
        self.stream.stop()


class _LiveTestTracker:
    def __init__(self, **_kwargs):
        pass

    def reset(self):
        pass

    def evaluate_worker_event(self, _worker):
        return {
            "should_record": True,
            "category": "Sin Casco",
            "title": "Prueba temporal",
            "status": "danger",
            "worker_id": "worker-1",
        }

    def purge_inactive_tracks(self):
        pass


if __name__ == "__main__":
    unittest.main()
