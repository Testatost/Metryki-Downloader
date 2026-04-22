from __future__ import annotations

import sys

from PyQt6.QtWidgets import QApplication, QStyleFactory

from metrykidownloader.app_constants import APP_DISPLAY_NAME, APP_FONT
from metrykidownloader.icons import set_windows_app_id
from metrykidownloader.main_window import MainWindow


def main() -> int:
    set_windows_app_id()
    app = QApplication(sys.argv)
    app.setApplicationName(APP_DISPLAY_NAME)
    app.setApplicationDisplayName(APP_DISPLAY_NAME)
    app.setFont(APP_FONT)

    fusion = QStyleFactory.create("Fusion")
    if fusion is not None:
        app.setStyle(fusion)

    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
