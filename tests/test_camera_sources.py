"""Pruebas unitarias para modules/camera_sources.py."""

import unittest
from unittest.mock import MagicMock, patch

from modules.camera_sources import (
    CAMERA_OPTIONS,
    STREAM_PRESETS,
    get_camera_options,
    normalize_stream_url,
    resolve_camera_source,
    scan_available_cameras,
)


class CameraSourcesTests(unittest.TestCase):
    def test_camera_options_contains_standard_entries(self):
        self.assertEqual(CAMERA_OPTIONS[0], "Cam-0: Integrada / Predeterminada")
        self.assertEqual(CAMERA_OPTIONS[1], "Cam-1: Webcam Externa USB (Feria)")
        self.assertEqual(CAMERA_OPTIONS[2], "Cam-2: Dispositivo Secundario USB")
        self.assertEqual(CAMERA_OPTIONS[3], "Flujo RTSP / IP")

    def test_normalize_stream_url(self):
        self.assertEqual(
            normalize_stream_url("http://192.168.1.50:8080"),
            "http://192.168.1.50:8080/video",
        )
        self.assertEqual(
            normalize_stream_url("http://192.168.1.50:8080/"),
            "http://192.168.1.50:8080/video",
        )
        self.assertEqual(
            normalize_stream_url("http://192.168.1.50:4747"),
            "http://192.168.1.50:4747/video",
        )
        self.assertEqual(
            normalize_stream_url("http://192.168.1.50:8080/video"),
            "http://192.168.1.50:8080/video",
        )
        self.assertEqual(
            normalize_stream_url("rtsp://192.168.1.50:554/live"),
            "rtsp://192.168.1.50:554/live",
        )
        self.assertEqual(normalize_stream_url("   "), "")

    def test_resolve_camera_source_standard(self):
        source, desc = resolve_camera_source(CAMERA_OPTIONS[0])
        self.assertEqual(source, 0)
        self.assertEqual(desc, "Cámara 0")

        source, desc = resolve_camera_source(CAMERA_OPTIONS[1])
        self.assertEqual(source, 1)
        self.assertEqual(desc, "Cámara 1")

        source, desc = resolve_camera_source(CAMERA_OPTIONS[2])
        self.assertEqual(source, 2)
        self.assertEqual(desc, "Cámara 2")

        source, desc = resolve_camera_source(
            CAMERA_OPTIONS[3], " http://192.168.1.10:8080 "
        )
        self.assertEqual(source, "http://192.168.1.10:8080/video")
        self.assertEqual(desc, "Flujo IP")

    def test_resolve_camera_source_dynamic_index(self):
        source, desc = resolve_camera_source("Cam-3: Dispositivo USB Adicional")
        self.assertEqual(source, 3)
        self.assertEqual(desc, "Cámara 3")

        source, desc = resolve_camera_source("Cam-4: Galaxy S24 FE UVC")
        self.assertEqual(source, 4)
        self.assertEqual(desc, "Cámara 4")

    def test_resolve_camera_source_invalid_raises_value_error(self):
        with self.assertRaises(ValueError):
            resolve_camera_source("Dispositivo Inexistente")

    def test_get_camera_options_default_and_extended(self):
        default_opts = get_camera_options()
        self.assertEqual(default_opts, CAMERA_OPTIONS)

        extended_opts = get_camera_options([0, 1, 3])
        self.assertIn("Cam-3: Dispositivo USB Adicional", extended_opts)
        self.assertEqual(extended_opts[-1], "Flujo RTSP / IP")

    def test_stream_presets_valid(self):
        self.assertIn("IP Webcam (Android :8080)", STREAM_PRESETS)
        self.assertIn("DroidCam (Android/iOS :4747)", STREAM_PRESETS)
        self.assertIn("RTSP Seguridad (:554)", STREAM_PRESETS)

    @patch("modules.camera_sources.cv2.VideoCapture")
    def test_scan_available_cameras(self, mock_capture):
        fake_cap_open = MagicMock()
        fake_cap_open.isOpened.return_value = True

        fake_cap_closed = MagicMock()
        fake_cap_closed.isOpened.return_value = False

        def capture_side_effect(index, *args):
            if index in [0, 1, 3]:
                return fake_cap_open
            return fake_cap_closed

        mock_capture.side_effect = capture_side_effect

        detected = scan_available_cameras(max_indices=5, force_refresh=True)
        self.assertEqual(detected, [0, 1, 3])


if __name__ == "__main__":
    unittest.main()
