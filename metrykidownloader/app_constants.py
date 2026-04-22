from __future__ import annotations

import os

from PyQt6.QtGui import QFont

APP_DISPLAY_NAME = "Metryki Downloader"
APP_TITLE = f" {APP_DISPLAY_NAME}"
APP_HOME_LABEL = "🏠 Metryki Genealodzy"
APP_HOME_URL = "https://metryki.genealodzy.pl/"
SETTINGS_ORG = "Testatost"
SETTINGS_APP = "MetrykiDownloader"
DEFAULT_HEADERS = {"User-Agent": "metryki-downloader/GUI"}
APP_FONT = QFont("Segoe UI", 10)

APP_VERSION = "1.6"
APP_AUTHOR = "Sebastian (Testatost)"
APP_GITHUB_URL = "https://github.com/Testatost/Metryki-Downloader"
APP_ID = "Sebastian.Testatost.MetrykiDownloader.1.6"

PACKAGE_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.dirname(PACKAGE_DIR)
ICON_PATH = os.path.join(PROJECT_ROOT, "icon.ico")
