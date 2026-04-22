from __future__ import annotations

import ctypes
import os
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QIcon, QLinearGradient, QPainter, QPen, QPixmap

from metrykidownloader.app_constants import APP_DISPLAY_NAME, APP_ID


def resource_path(filename: str) -> str:
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(sys.argv[0])))
    return os.path.join(base_path, filename)


def get_app_icon() -> QIcon:
    icon = QIcon()

    preferred = ("icon.ico", "icon.png", "logo.png") if sys.platform.startswith("win") else ("icon.png", "icon.ico", "logo.png")
    for filename in preferred:
        path = resource_path(filename)
        if os.path.exists(path):
            icon.addFile(path)

    return icon


def set_windows_app_id() -> None:
    if sys.platform.startswith("win"):
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)
        except Exception:
            pass


def get_banner_pixmap(width: int = 680, height: int = 120) -> QPixmap:
    for filename in ("banner.png", "banner.jpg", "banner.jpeg", "header.png"):
        path = resource_path(filename)
        if os.path.exists(path):
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                return pixmap.scaled(width, height, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)

    pixmap = QPixmap(width, height)
    pixmap.fill(QColor("#00000000"))

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

    gradient = QLinearGradient(0, 0, width, height)
    gradient.setColorAt(0.0, QColor("#16324f"))
    gradient.setColorAt(1.0, QColor("#2f6da3"))
    painter.setBrush(gradient)
    painter.setPen(Qt.PenStyle.NoPen)
    painter.drawRoundedRect(0, 0, width, height, 18, 18)

    painter.setPen(QPen(QColor("#ffffff")))
    title_font = QFont("Segoe UI", max(14, height // 5), int(QFont.Weight.Bold))
    painter.setFont(title_font)
    painter.drawText(28, 24, width - 56, height - 48, int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter), APP_DISPLAY_NAME)

    subtitle_font = QFont("Segoe UI", max(9, height // 10))
    painter.setFont(subtitle_font)
    painter.drawText(30, height - 36, width - 60, 24, int(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter), "Metryki Genealodzy • GUI Downloader")

    painter.end()
    return pixmap
