"""Vistas modulares y componentes de interfaz para Vigilante EPP."""

from modules.views.components import (
    render_stream_presets,
    render_device_scanner,
    render_desktop_window_card,
)
from modules.views.config_dialog import config_dialog
from modules.views.demo_view import render_demo_view
from modules.views.live_view import render_live_view
from modules.views.stats_view import render_stats_view
from modules.views.reports_view import render_reports_view

__all__ = [
    "render_stream_presets",
    "render_device_scanner",
    "render_desktop_window_card",
    "config_dialog",
    "render_demo_view",
    "render_live_view",
    "render_stats_view",
    "render_reports_view",
]
