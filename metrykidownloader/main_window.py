from __future__ import annotations

import json
import os
from datetime import datetime

from PyQt6.QtCore import QSettings, Qt, QUrl, pyqtSlot
from PyQt6.QtGui import QAction, QDesktopServices, QIcon
from PyQt6.QtWidgets import (
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QHeaderView,
    QInputDialog,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QRadioButton,
    QStatusBar,
    QStyleFactory,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
    QButtonGroup,
)

from metrykidownloader.app_constants import APP_HOME_URL, ICON_PATH, SETTINGS_APP, SETTINGS_ORG
from metrykidownloader.i18n import LANG
from metrykidownloader.models import BookEntry
from metrykidownloader.styles import dark_stylesheet, light_stylesheet
from metrykidownloader.worker import DownloaderWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings(SETTINGS_ORG, SETTINGS_APP)
        self.lang = self._load_language_setting()
        self.is_dark = self._load_theme_setting()
        self.books: list[BookEntry] = []
        self.worker: DownloaderWorker | None = None

        if os.path.exists(ICON_PATH):
            self.setWindowIcon(QIcon(ICON_PATH))

        self.setWindowTitle(self._t("title"))
        self.resize(1000, 900)
        self.setMinimumSize(900, 620)

        fusion = QStyleFactory.create("Fusion")
        if fusion is not None:
            self.setStyle(fusion)

        self._build_ui()
        self.apply_theme()
        self.retranslate_ui()
        self._status_message("status_ready")

    def _t(self, key: str) -> str:
        return LANG[self.lang][key]

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)

        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)

        top_bar = QHBoxLayout()
        top_bar.setSpacing(10)

        self.btn_home = QPushButton()
        self.btn_home.clicked.connect(self.open_home)
        top_bar.addWidget(self.btn_home)

        self.btn_theme = QPushButton()
        self.btn_theme.setFixedSize(46, 40)
        self.btn_theme.clicked.connect(self.toggle_theme)
        top_bar.addWidget(self.btn_theme)

        top_bar.addStretch(1)

        self.lang_group = QButtonGroup(self)
        self.rb_de = QRadioButton("DE")
        self.rb_en = QRadioButton("EN")
        self.rb_pl = QRadioButton("PL")

        for rb, value in ((self.rb_de, "de"), (self.rb_en, "en"), (self.rb_pl, "pl")):
            self.lang_group.addButton(rb)
            rb.toggled.connect(lambda checked, v=value: self.on_language_toggled(v, checked))
            top_bar.addWidget(rb)

        for rb in (self.rb_de, self.rb_en, self.rb_pl):
            rb.blockSignals(True)
        if self.lang == "de":
            self.rb_de.setChecked(True)
        elif self.lang == "en":
            self.rb_en.setChecked(True)
        else:
            self.rb_pl.setChecked(True)
        for rb in (self.rb_de, self.rb_en, self.rb_pl):
            rb.blockSignals(False)

        main_layout.addLayout(top_bar)

        input_group = QGroupBox()
        input_layout = QGridLayout(input_group)
        input_layout.setHorizontalSpacing(12)
        input_layout.setVerticalSpacing(10)

        self.lbl_url = QLabel()
        self.url_entry = QLineEdit()
        self.url_entry.setPlaceholderText("https://metryki.genealodzy.pl/…")
        input_layout.addWidget(self.lbl_url, 0, 0)
        input_layout.addWidget(self.url_entry, 0, 1, 1, 3)

        self.lbl_outdir = QLabel()
        self.outdir_entry = QLineEdit()
        last_outdir = str(self.settings.value("ui/last_outdir", "") or "").strip()
        if last_outdir:
            self.outdir_entry.setText(last_outdir)
        input_layout.addWidget(self.lbl_outdir, 1, 0)
        input_layout.addWidget(self.outdir_entry, 1, 1, 1, 2)

        self.btn_choose = QPushButton()
        self.btn_choose.clicked.connect(self.choose_dir)
        input_layout.addWidget(self.btn_choose, 1, 3)

        self.lbl_pages = QLabel()
        self.pages_entry = QLineEdit()
        input_layout.addWidget(self.lbl_pages, 2, 0)
        input_layout.addWidget(self.pages_entry, 2, 1)

        self.lbl_pages_hint = QLabel()
        self.lbl_pages_hint.setObjectName("hintLabel")
        input_layout.addWidget(self.lbl_pages_hint, 2, 2, 1, 2)

        main_layout.addWidget(input_group)

        self.btn_add_book = QPushButton()
        self.btn_add_book.setObjectName("addBookButton")
        self.btn_add_book.clicked.connect(self.add_book)

        self.btn_delete_book = QPushButton()
        self.btn_delete_book.setObjectName("deleteBookButton")
        self.btn_delete_book.clicked.connect(self.delete_book)

        self.btn_change_pages = QPushButton()
        self.btn_change_pages.setObjectName("changePagesButton")
        self.btn_change_pages.clicked.connect(self.change_pages)

        self.btn_download = QPushButton()
        self.btn_download.setObjectName("downloadButton")
        self.btn_download.clicked.connect(self.start_books)

        self.btn_stop = QPushButton()
        self.btn_stop.setObjectName("stopButton")
        self.btn_stop.clicked.connect(self.stop_download)

        self.btn_reset = QPushButton()
        self.btn_reset.setObjectName("resetButton")
        self.btn_reset.clicked.connect(self.reset_books)

        self.btn_save_list = QPushButton()
        self.btn_save_list.clicked.connect(self.save_list)

        self.btn_load_list = QPushButton()
        self.btn_load_list.clicked.connect(self.load_list)

        self.btn_export_pdf = QPushButton()
        self.btn_export_pdf.clicked.connect(self.export_pdf)

        self.btn_save_log = QPushButton()
        self.btn_save_log.clicked.connect(self.save_log_to_file)

        self.btn_log_toggle = QPushButton()
        self.btn_log_toggle.clicked.connect(self.toggle_log)

        action_rows = []
        for _ in range(3):
            row = QHBoxLayout()
            row.setSpacing(10)
            action_rows.append(row)
            main_layout.addLayout(row)

        action_rows[0].addStretch(1)
        for button in (self.btn_add_book, self.btn_delete_book, self.btn_change_pages):
            button.setMinimumHeight(42)
            button.setMinimumWidth(185)
            action_rows[0].addWidget(button)
        action_rows[0].addStretch(1)

        action_rows[1].addStretch(1)
        for button in (self.btn_download, self.btn_stop, self.btn_reset):
            button.setMinimumHeight(42)
            button.setMinimumWidth(185)
            action_rows[1].addWidget(button)
        action_rows[1].addStretch(1)

        action_rows[2].addStretch(1)
        for button in (self.btn_save_list, self.btn_load_list, self.btn_export_pdf, self.btn_save_log, self.btn_log_toggle):
            button.setMinimumHeight(40)
            button.setMinimumWidth(155)
            action_rows[2].addWidget(button)
        action_rows[2].addStretch(1)

        self.lbl_waiting = QLabel()
        main_layout.addWidget(self.lbl_waiting)

        self.table = QTableWidget(0, 3)
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.ExtendedSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.cellDoubleClicked.connect(self.open_book_url)
        self.table.setMinimumHeight(320)
        main_layout.addWidget(self.table, 1)

        progress_row = QHBoxLayout()
        self.lbl_progress = QLabel()
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_label = QLabel("0%")
        self.progress_label.setMinimumWidth(48)
        progress_row.addWidget(self.lbl_progress)
        progress_row.addWidget(self.progress_bar, 1)
        progress_row.addWidget(self.progress_label)
        main_layout.addLayout(progress_row)

        self.log_container = QGroupBox()
        self.log_container_layout = QVBoxLayout(self.log_container)
        self.log_container_layout.setContentsMargins(8, 8, 8, 8)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMinimumHeight(160)
        self.log_container_layout.addWidget(self.log_text)
        main_layout.addWidget(self.log_container)
        self.log_container.hide()

        delete_action = QAction(self)
        delete_action.setShortcut("Delete")
        delete_action.triggered.connect(self.delete_book)
        self.addAction(delete_action)

        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.btn_stop.setEnabled(False)

    def _load_theme_setting(self) -> bool:
        value = self.settings.value("ui/is_dark", False)
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() in ("1", "true", "yes", "on")

    def _save_theme_setting(self) -> None:
        self.settings.setValue("ui/is_dark", self.is_dark)

    def _load_language_setting(self) -> str:
        value = str(self.settings.value("ui/lang", "de") or "de").strip().lower()
        return value if value in LANG else "de"

    def _save_language_setting(self) -> None:
        self.settings.setValue("ui/lang", self.lang)

    def apply_theme(self) -> None:
        self.setStyleSheet(dark_stylesheet() if self.is_dark else light_stylesheet())
        self.btn_theme.setText("☀️" if self.is_dark else "🪩")
        self.btn_theme.setToolTip(self._t("theme_light") if self.is_dark else self._t("theme_dark"))

    @pyqtSlot()
    def toggle_theme(self) -> None:
        self.is_dark = not self.is_dark
        self._save_theme_setting()
        self.apply_theme()

    @pyqtSlot()
    def open_home(self) -> None:
        QDesktopServices.openUrl(QUrl(APP_HOME_URL))

    @pyqtSlot(str, bool)
    def on_language_toggled(self, lang: str, checked: bool) -> None:
        if checked:
            self.lang = lang
            self._save_language_setting()
            self.retranslate_ui()

    def retranslate_ui(self) -> None:
        self.setWindowTitle(self._t("title"))
        self.btn_home.setText(self._t("home"))
        self.btn_add_book.setText(self._t("add_book"))
        self.btn_delete_book.setText(self._t("delete_book"))
        self.btn_change_pages.setText(self._t("change_pages"))
        self.btn_download.setText(self._t("download"))
        self.btn_stop.setText(self._t("stop"))
        self.btn_reset.setText(self._t("reset"))
        self.btn_save_list.setText(self._t("save_list"))
        self.btn_load_list.setText(self._t("load_list"))
        self.btn_export_pdf.setText(self._t("export_pdf"))
        self.btn_save_log.setText(self._t("save_log"))
        self.btn_log_toggle.setText(self._t("hide_log") if self.log_container.isVisible() else self._t("show_log"))
        self.btn_choose.setText(self._t("choose_dir"))
        self.lbl_url.setText(self._t("book_url"))
        self.lbl_outdir.setText(self._t("target_dir"))
        self.lbl_pages.setText(self._t("pages"))
        self.lbl_pages_hint.setText(self._t("pages_hint"))
        self.lbl_waiting.setText(self._t("waiting_list"))
        self.lbl_progress.setText(self._t("global_progress"))
        self.table.setHorizontalHeaderLabels([self._t("col_url"), self._t("col_pages"), self._t("col_status")])
        self.log_container.setTitle(self._t("log_title"))
        self.apply_theme()

    def _status_message(self, key: str) -> None:
        self.statusBar().showMessage(self._t(key))

    def log(self, msg: str) -> None:
        line = f"{datetime.now().strftime('%H:%M:%S')} {msg}"
        self.log_text.append(line)

    @pyqtSlot()
    def save_log_to_file(self) -> None:
        content = self.log_text.toPlainText().strip()
        if not content:
            QMessageBox.information(self, self._t("title"), self._t("log_empty"))
            return

        default_name = os.path.join(os.getcwd(), self._t("save_log_default"))
        path, _ = QFileDialog.getSaveFileName(self, self._t("save_log"), default_name, "Text (*.txt)")
        if not path:
            return

        try:
            with open(path, "w", encoding="utf-8") as handle:
                handle.write(content + "\n")
            QMessageBox.information(self, self._t("title"), self._t("log_saved"))
        except Exception as exc:
            QMessageBox.critical(self, self._t("title"), str(exc))

    @pyqtSlot()
    def toggle_log(self) -> None:
        visible = not self.log_container.isVisible()
        self.log_container.setVisible(visible)
        self.btn_log_toggle.setText(self._t("hide_log") if visible else self._t("show_log"))

    @pyqtSlot()
    def choose_dir(self) -> None:
        start_dir = self.outdir_entry.text().strip() or os.getcwd()
        selected = QFileDialog.getExistingDirectory(self, self._t("choose_dir"), start_dir)
        if selected:
            self.outdir_entry.setText(selected)
            self.settings.setValue("ui/last_outdir", selected)

    @pyqtSlot()
    def add_book(self) -> None:
        url = self.url_entry.text().strip()
        outdir = self.outdir_entry.text().strip() or str(self.settings.value("ui/last_outdir", "") or "").strip() or os.getcwd()
        pages = self.pages_entry.text().strip()

        if not url:
            QMessageBox.warning(self, self._t("title"), self._t("error_no_url"))
            return
        if not os.path.isdir(outdir):
            QMessageBox.warning(self, self._t("title"), self._t("error_no_outdir"))
            return

        book = BookEntry(url=url, outdir=outdir, pages=pages)
        self.books.append(book)
        self._append_table_row(book)
        self.log(f"[+] URL hinzugefügt: {url}")

        self.url_entry.clear()
        self.pages_entry.clear()
        self.url_entry.setFocus()

    def _append_table_row(self, book: BookEntry) -> None:
        row = self.table.rowCount()
        self.table.insertRow(row)

        url_item = QTableWidgetItem(book.url)
        pages_item = QTableWidgetItem(book.pages or "ALL")
        status_item = QTableWidgetItem("⏳")

        pages_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

        self.table.setItem(row, 0, url_item)
        self.table.setItem(row, 1, pages_item)
        self.table.setItem(row, 2, status_item)

    @pyqtSlot()
    def delete_book(self) -> None:
        selected = sorted({index.row() for index in self.table.selectionModel().selectedRows()}, reverse=True)
        if not selected:
            QMessageBox.warning(self, self._t("title"), self._t("error_no_selection"))
            return

        for row in selected:
            del self.books[row]
            self.table.removeRow(row)

        self.log("[-] Eintrag gelöscht.")

    @pyqtSlot()
    def change_pages(self) -> None:
        selected = sorted({index.row() for index in self.table.selectionModel().selectedRows()})
        if not selected:
            QMessageBox.warning(self, self._t("title"), self._t("error_no_selection"))
            return

        row = selected[0]
        current_pages = self.books[row].pages
        pages, ok = QInputDialog.getText(
            self,
            self._t("pages_dialog_title"),
            self._t("pages_hint"),
            text=current_pages,
        )
        if ok:
            pages = pages.strip()
            self.books[row].pages = pages
            self.table.item(row, 1).setText(pages or "ALL")
            self.log(f"[~] Seiten geändert: {self.books[row].url} -> {pages or 'ALL'}")

    @pyqtSlot(int, int)
    def open_book_url(self, row: int, _column: int) -> None:
        item = self.table.item(row, 0)
        if item and item.text():
            QDesktopServices.openUrl(QUrl(item.text()))

    @pyqtSlot()
    def reset_books(self) -> None:
        if self.worker and self.worker.isRunning():
            QMessageBox.warning(self, self._t("title"), self._t("error_running_reset"))
            return

        self.books.clear()
        self.table.setRowCount(0)
        self.progress_bar.setValue(0)
        self.progress_label.setText("0%")
        self.log("[*] Warteliste zurückgesetzt.")

    @pyqtSlot()
    def save_list(self) -> None:
        if not self.books:
            return

        default_name = os.path.join(os.getcwd(), self._t("save_list_default"))
        path, _ = QFileDialog.getSaveFileName(self, self._t("save_list"), default_name, "JSON (*.json)")
        if not path:
            return

        with open(path, "w", encoding="utf-8") as handle:
            json.dump([book.to_dict() for book in self.books], handle, indent=2, ensure_ascii=False)

        self.log(f"[💾] Warteliste gespeichert: {path}")

    @pyqtSlot()
    def load_list(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, self._t("load_list"), os.getcwd(), "JSON (*.json)")
        if not path:
            return

        with open(path, "r", encoding="utf-8") as handle:
            raw_books = json.load(handle)

        self.books = [BookEntry.from_dict(item) for item in raw_books]
        self.table.setRowCount(0)
        for book in self.books:
            self._append_table_row(book)

        self.log(f"[📂] Warteliste geladen: {path}")

    @pyqtSlot()
    def export_pdf(self) -> None:
        try:
            from PIL import Image
        except Exception as exc:
            QMessageBox.critical(self, self._t("title"), str(exc))
            return

        unique_outdirs = sorted({book.outdir for book in self.books if book.outdir and os.path.isdir(book.outdir)})
        if not unique_outdirs:
            QMessageBox.information(self, self._t("title"), self._t("pdf_none"))
            return

        pdf_count = 0
        for outdir in unique_outdirs:
            for root, _dirs, files in os.walk(outdir):
                jpg_files = sorted(
                    os.path.join(root, filename)
                    for filename in files
                    if filename.lower().endswith(".jpg")
                )
                if not jpg_files:
                    continue

                images = []
                for image_path in jpg_files:
                    try:
                        with Image.open(image_path) as img:
                            images.append(img.convert("RGB"))
                    except Exception as exc:
                        self.log(f"[!] PDF Fehler bei {image_path}: {exc}")

                if not images:
                    continue

                pdf_path = os.path.join(root, f"{os.path.basename(root)}.pdf")
                try:
                    images[0].save(pdf_path, save_all=True, append_images=images[1:])
                    pdf_count += 1
                    self.log(f"[📄] PDF erzeugt: {pdf_path}")
                except Exception as exc:
                    self.log(f"[!] PDF Fehler: {exc}")
                finally:
                    for image in images:
                        image.close()

        QMessageBox.information(self, self._t("title"), self._t("pdf_done") if pdf_count else self._t("pdf_none"))

    def _set_running_state(self, running: bool) -> None:
        self.btn_add_book.setEnabled(not running)
        self.btn_delete_book.setEnabled(not running)
        self.btn_change_pages.setEnabled(not running)
        self.btn_download.setEnabled(not running)
        self.btn_reset.setEnabled(not running)
        self.btn_save_list.setEnabled(not running)
        self.btn_load_list.setEnabled(not running)
        self.btn_export_pdf.setEnabled(not running)
        self.btn_save_log.setEnabled(not running)
        self.btn_choose.setEnabled(not running)
        self.url_entry.setEnabled(not running)
        self.outdir_entry.setEnabled(not running)
        self.pages_entry.setEnabled(not running)
        self.btn_stop.setEnabled(running)

    @pyqtSlot()
    def start_books(self) -> None:
        if not self.books:
            QMessageBox.warning(self, self._t("title"), self._t("error_no_book"))
            return

        if self.worker and self.worker.isRunning():
            return

        self.progress_bar.setValue(0)
        self.progress_label.setText("0%")
        self._set_running_state(True)

        for row in range(self.table.rowCount()):
            self.table.item(row, 2).setText("⏳")

        self.worker = DownloaderWorker(
            books=[BookEntry(url=book.url, outdir=book.outdir, pages=book.pages) for book in self.books],
            parent=self,
        )
        self.worker.log_message.connect(self.log)
        self.worker.book_status.connect(self.update_book_status)
        self.worker.global_progress.connect(self.update_global_progress)
        self.worker.finished_signal.connect(self.on_worker_finished)
        self.worker.start()

        self._status_message("status_running")

    @pyqtSlot()
    def stop_download(self) -> None:
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self._status_message("status_stopped")

    @pyqtSlot(int, str)
    def update_book_status(self, row: int, value: str) -> None:
        item = self.table.item(row, 2)
        if item:
            item.setText(value)

    @pyqtSlot(float)
    def update_global_progress(self, value: float) -> None:
        int_value = max(0, min(100, int(round(value))))
        self.progress_bar.setValue(int_value)
        self.progress_label.setText(f"{int_value}%")

    @pyqtSlot()
    def on_worker_finished(self) -> None:
        self._set_running_state(False)
        self._status_message("status_finished")
        self.worker = None

    def closeEvent(self, event) -> None:
        self._save_theme_setting()
        self._save_language_setting()
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            self.worker.wait(2000)
        event.accept()
