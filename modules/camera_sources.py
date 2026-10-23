"""Opciones de cámara compartidas por análisis en vivo y demostración."""

import re
import threading
import time
import cv2


CAMERA_MODE_LOCK = threading.Lock()

CAMERA_OPTIONS = (
    "Cam-0: Integrada / Predeterminada",
    "Cam-1: Webcam Externa USB (Feria)",
    "Cam-2: Dispositivo Secundario USB",
    "Flujo RTSP / IP",
)

STREAM_PRESETS = {
    "IP Webcam (Android :8080)": "http://192.168.1.50:8080/video",
    "DroidCam (Android/iOS :4747)": "http://192.168.1.50:4747/video",
    "RTSP Seguridad (:554)": "rtsp://192.168.1.50:554/live",
}

_CACHED_AVAILABLE_CAMERAS = None
_LAST_SCAN_TIME = 0.0
_SCAN_CACHE_TTL = 15.0


def normalize_stream_url(url: str) -> str:
    """
    Normaliza la dirección de red para flujos IP comunes.
    Agrega el endpoint de video automáticamente si el usuario ingresa solo host y puerto.
    """
    cleaned = url.strip()
    if not cleaned:
        return ""
    if re.match(r"^https?://[a-zA-Z0-9.\-_]+:(8080|4747)/?$", cleaned, re.IGNORECASE):
        cleaned = cleaned.rstrip("/") + "/video"
    return cleaned


def scan_available_cameras(max_indices=4, force_refresh=False):
    """
    Sondea de forma no bloqueante o con caché los puertos DirectShow
    para detectar cámaras USB y dispositivos UVC conectados.
    """
    global _CACHED_AVAILABLE_CAMERAS, _LAST_SCAN_TIME
    now = time.monotonic()
    if not force_refresh and _CACHED_AVAILABLE_CAMERAS is not None and (now - _LAST_SCAN_TIME < _SCAN_CACHE_TTL):
        return _CACHED_AVAILABLE_CAMERAS

    detected = []
    for idx in range(max_indices):
        try:
            cap = cv2.VideoCapture(idx, cv2.CAP_DSHOW)
            if cap.isOpened():
                detected.append(idx)
                cap.release()
        except Exception:
            pass

    _CACHED_AVAILABLE_CAMERAS = detected
    _LAST_SCAN_TIME = now
    return detected


def get_camera_options(detected_indices=None):
    """
    Construye las opciones de cámara integrando los puertos estándar
    y cualquier índice adicional detectado en el sistema (> 2).
    """
    options = list(CAMERA_OPTIONS[:3])
    if detected_indices:
        for idx in detected_indices:
            if idx > 2:
                opt_name = f"Cam-{idx}: Dispositivo USB Adicional"
                if opt_name not in options:
                    options.append(opt_name)
    options.append(CAMERA_OPTIONS[3])
    return tuple(options)


def resolve_camera_source(choice, stream_url=""):
    """Obtiene la fuente OpenCV y una descripción sin exponer la URL IP."""
    if choice.startswith("Cam-") and ":" in choice:
        try:
            idx_str = choice.split(":")[0].replace("Cam-", "").strip()
            camera_index = int(idx_str)
            return camera_index, f"Cámara {camera_index}"
        except ValueError:
            pass

    if choice in CAMERA_OPTIONS[:3]:
        camera_index = CAMERA_OPTIONS.index(choice)
        return camera_index, f"Cámara {camera_index}"

    if choice == CAMERA_OPTIONS[3] or "RTSP / IP" in choice:
        cleaned_url = normalize_stream_url(stream_url)
        return cleaned_url, "Flujo IP"

    raise ValueError("La cámara seleccionada no está disponible.")

