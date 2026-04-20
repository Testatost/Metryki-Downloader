from __future__ import annotations

import os

from PyQt6.QtGui import QFont

APP_DISPLAY_NAME = "Metryki Downloader"
APP_TITLE = APP_DISPLAY_NAME
APP_HOME_LABEL = "🏠 Metryki Genealodzy"
APP_HOME_URL = "https://metryki.genealodzy.pl/"
SETTINGS_ORG = "Testatost"
SETTINGS_APP = "MetrykiDownloader"
DEFAULT_HEADERS = {"User-Agent": "metryki-downloader/2.0"}
APP_FONT = QFont("Segoe UI", 10)

APP_VERSION = "2.0"
APP_AUTHOR = "Sebastian (Testatost)"

PACKAGE_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(PACKAGE_DIR)
ICON_PATH = os.path.join(PROJECT_ROOT, "icon.ico")
