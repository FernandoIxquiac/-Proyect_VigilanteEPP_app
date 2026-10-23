"""Comprueba navegación y cambios de visor sin abrir cámara ni base operativa."""

import os
import subprocess
import sys
import textwrap
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class AppNavigationTests(unittest.TestCase):
    def test_navigation_sources_and_destinations_remain_usable(self):
        script = textwrap.dedent(
            """
            import os
            import tempfile

            from streamlit.testing.v1 import AppTest

            import modules.auditor as auditor_module
            import modules.database as database_module
            import modules.demo_video as demo_module
            import modules.detector as detector_module


            class FakeAuditor:
                def __init__(self):
                    self.active = False
                    self.native = False
                    self.starts = []
                    self.fail_next_start = True

                def set_theme(self, is_dark):
                    pass

                def get_theme(self):
                    return True

                def is_running(self):
                    return self.active

                def is_busy(self):
                    return self.active

                def update_config(self, *args, **config):
                    pass

                def set_native_window(self, enabled):
                    self.native = enabled

                def start(self, **config):
                    self.starts.append(config)
                    if self.fail_next_start:
                        self.fail_next_start = False
                        return False
                    self.active = True
                    return True

                def stop(self):
                    self.active = False

                def get_latest_state(self):
                    return {
                        "is_running": self.active,
                        "frame_bytes": None,
                        "status": "safe" if self.active else "standby",
                        "title": "ACTIVO",
                        "message": "Prueba",
                        "session_events": 0,
                        "session_infractions": 0,
                        "session_id": 1,
                        "persons_count": 0,
                    }


            auditor = FakeAuditor()
            auditor_module.get_live_auditor = lambda: auditor


            class FakeDemoVideo:
                def __init__(self):
                    self.active = False
                    self.starts = []
                    self.stops = 0
                    self.run_id = 0

                def is_running(self):
                    return self.active

                def is_busy(self):
                    return self.active

                def get_run_id(self):
                    return self.run_id

                def get_state(self):
                    return {
                        "status": "running" if self.active else "standby",
                        "message": "Prueba",
                        "persons_count": 0,
                        "detections_count": 0,
                        "fps": 0.0,
                    }

                def update_config(self, *args, **config):
                    pass

                def start(self, **config):
                    self.starts.append(config)
                    self.active = True
                    self.run_id += 1
                    return True

                def stop(self):
                    self.stops += 1
                    self.active = False
                    self.run_id += 1
                    return True


            demo_video = FakeDemoVideo()
            demo_module.get_demo_video_service = lambda: demo_video
            detector_module.load_detector_model = lambda: (object(), "Prueba")

            with tempfile.TemporaryDirectory(prefix="epp-app-test-") as temp_dir:
                database_module.DB_PATH = os.path.join(temp_dir, "test.db")
                database_module.CAPTURES_DIR = os.path.join(temp_dir, "captures")
                os.makedirs(database_module.CAPTURES_DIR, exist_ok=True)

                app = AppTest.from_file("app.py", default_timeout=30)
                app.query_params["current_page"] = "live"
                app.run()
                assert app.session_state["current_page"] == "Analisis en Vivo"
                assert "current_page" not in app.query_params
                assert not app.exception

                for key, expected in (
                    ("nav_btn_stats", "Estadisticas"),
                    ("nav_btn_reports", "Reportes"),
                    ("nav_btn_demo", "Demostracion"),
                    ("nav_btn_live", "Analisis en Vivo"),
                ):
                    app.button(key=key).click().run()
                    assert app.session_state["current_page"] == expected
                    assert not app.exception

                def _toggle_demo(val=True):
                    if app.toggle:
                        app.toggle(key="demo_power_toggle").set_value(val).run()
                    else:
                        app.button(key="demo_video_start").click().run()

                app.button(key="nav_btn_demo").click().run()
                app.selectbox(key="demo_camera_selector").set_value(
                    "Cam-1: Webcam Externa USB (Feria)"
                ).run()
                _toggle_demo(True)
                assert demo_video.active
                assert demo_video.starts[-1]["source"] == 1
                assert not app.exception
                observer = AppTest.from_file("app.py", default_timeout=30)
                observer.session_state["current_page"] = "Estadisticas"
                observer.run()
                assert demo_video.active
                assert demo_video.stops == 0
                assert not observer.exception
                app.button(key="nav_btn_stats").click().run()
                assert demo_video.stops == 1
                assert not demo_video.active
                assert not app.exception
                app.button(key="nav_btn_live").click().run()

                app.selectbox[0].set_value(
                    "Cam-1: Webcam Externa USB (Feria)"
                ).run()
                assert not app.radio
                app.button(key="nav_btn_stats").click().run()
                app.button(key="nav_btn_live").click().run()
                assert app.session_state["camera_source_choice"].startswith("Cam-1")

                def _toggle_camera(val=True):
                    if app.toggle:
                        app.toggle(key="camera_power_toggle").set_value(val).run()
                    else:
                        app.button[0].click().run()

                _toggle_camera(True)
                assert auditor.starts[-1]["source"] == 1
                assert not auditor.active
                assert app.error
                assert not app.exception

                _toggle_camera(True)
                assert auditor.starts[-1]["source"] == 1
                assert auditor.starts[-1]["show_native_window"]
                assert auditor.active
                assert not app.exception

                assert auditor.native
                assert not app.radio

                app.button(key="nav_btn_demo").click().run()
                _toggle_demo(True)
                assert not demo_video.active
                assert app.error
                assert not app.exception
                app.button(key="nav_btn_live").click().run()

                app.button(key="nav_btn_stats").click().run()
                assert app.session_state["current_page"] == "Estadisticas"
                assert not app.exception

                app.button(key="nav_btn_live").click().run()
                _toggle_camera(False)
                assert not auditor.active
                app.selectbox[0].set_value(
                    "Cam-2: Dispositivo Secundario USB"
                ).run()
                _toggle_camera(True)
                assert auditor.starts[-1]["source"] == 2
                assert auditor.starts[-1]["show_native_window"]
                assert auditor.active
                assert not app.exception

                auditor.stop()
                monitor = AppTest.from_file("app.py", default_timeout=30)
                monitor.query_params["view"] = "monitor"
                monitor.query_params["camera"] = "1"
                monitor.run()
                assert monitor.session_state["current_page"] == "Analisis en Vivo"
                assert monitor.session_state["camera_source_choice"].startswith("Cam-1")
                assert "view" not in monitor.query_params
                assert "camera" not in monitor.query_params
                assert not monitor.exception
            """
        )
        environment = os.environ.copy()
        environment["PYTHONIOENCODING"] = "utf-8"
        result = subprocess.run(
            [sys.executable, "-c", script],
            cwd=ROOT,
            env=environment,
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
