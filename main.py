import sys
import os
import time
import webbrowser
import requests
from urllib.parse import urlparse, parse_qs

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit,
    QLabel, QFileDialog, QLineEdit, QListWidget, QAbstractItemView, QProgressBar
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QIcon

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# ---------------- Übersetzungen ----------------
translations = {
    "Deutsch": {
        "title": "Metryki Downloader (Buch-Ordner pro URL)",
        "url_placeholder": "Haupt-URL eingeben (z. B. https://metryki.genealodzy.pl/id598-sy1904-kt1)",
        "add_button": "Hinzufügen",
        "folder_placeholder": "Zielordner eingeben oder wählen …",
        "folder_button": "Zielordner",
        "download_button": "Download",
        "stop_button": "Stopp",
        "reset_button": "Reset",
        "delete_button": "Löschen",
        "toggle_log_button": "Log ein/aus",
        "import_button": "Import Liste",
        "export_button": "Export Liste",
        "home_button": "🏠 Metryki Genealodzy",
        "progress_label": "Download-Fortschritt:",
        "log_label": "Log:",
        "log_added": "➕ URL hinzugefügt: {}",
        "log_folder": "📂 Zielordner gewählt: {}",
        "log_reset": "🔄 Warteliste zurückgesetzt.",
        "log_deleted": "❌ Gelöscht: {}",
        "log_no_selection": "ℹ️ Keine ausgewählten Einträge zum Löschen.",
        "log_imported": "📥 Warteliste importiert: {}",
        "log_exported": "📤 Warteliste exportiert: {}",
        "log_error_import": "❌ Fehler beim Import: {}",
        "log_error_export": "❌ Fehler beim Export: {}",
        "log_download_started": "⬇️ Download gestartet...",
        "log_download_running": "⚠️ Download läuft bereits.",
        "log_no_urls": "⚠️ Keine URLs in der Liste!",
        "log_no_folder": "⚠️ Kein gültiger Zielordner gewählt!",
        "log_download_finished": "🎉 Download-Fortschritt beendet.",
        "log_stop_requested": "⏹️ Stop angefordert.",
        "log_no_download": "ℹ️ Kein laufender Download zum Stoppen.",
        "log_open_main": "🌍 Öffne Hauptseite: {}",
        "log_unit_folder": "📂 Einheit-Ordner: {}",
        "log_pages_found": "📄 {} Seiten/Bilder gefunden.",
        "log_open_page": "[{}/{}] Öffne Bildseite: {}",
        "log_downloading": "⬇️ Herunterladen: {}",
        "log_saved": "✅ Gespeichert: {} ({}%)",
        "log_no_download_link": "⚠️ Kein Download-Link oder Bild-URL gefunden auf dieser Seite.",
        "log_network_error": "❌ Netzwerkfehler beim Herunterladen: {}",
        "log_http_error": "❌ Fehler beim Herunterladen: HTTP {}",
        "log_file_write_error": "❌ Fehler beim Schreiben der Datei: {}",
        "log_browser_error": "❌ Fehler beim Starten des Browsers: {}",
        "log_page_error": "❌ Fehler beim Laden der Seite: {}"
    },
    "English": {
        "title": "Metryki Downloader (Book Folder per URL)",
        "url_placeholder": "Enter main URL (e.g., https://metryki.genealodzy.pl/id598-sy1904-kt1)",
        "add_button": "Add",
        "folder_placeholder": "Enter or choose save folder …",
        "folder_button": "Save Folder",
        "download_button": "Download",
        "stop_button": "Stop",
        "reset_button": "Reset",
        "delete_button": "Delete",
        "toggle_log_button": "Toggle Log",
        "import_button": "Import List",
        "export_button": "Export List",
        "home_button": "🏠 Metryki Genealodzy",
        "progress_label": "Download Progress:",
        "log_label": "Log:",
        "log_added": "➕ URL added: {}",
        "log_folder": "📂 Save folder chosen: {}",
        "log_reset": "🔄 Queue reset.",
        "log_deleted": "❌ Deleted: {}",
        "log_no_selection": "ℹ️ No selected items to delete.",
        "log_imported": "📥 Queue imported: {}",
        "log_exported": "📤 Queue exported: {}",
        "log_error_import": "❌ Error during import: {}",
        "log_error_export": "❌ Error during export: {}",
        "log_download_started": "⬇️ Download started...",
        "log_download_running": "⚠️ Download already running.",
        "log_no_urls": "⚠️ No URLs in the list!",
        "log_no_folder": "⚠️ No valid save folder chosen!",
        "log_download_finished": "🎉 Download finished.",
        "log_stop_requested": "⏹️ Stop requested.",
        "log_no_download": "ℹ️ No running download to stop.",
        "log_open_main": "🌍 Opening main page: {}",
        "log_unit_folder": "📂 Unit folder: {}",
        "log_pages_found": "📄 {} pages/images found.",
        "log_open_page": "[{}/{}] Opening page: {}",
        "log_downloading": "⬇️ Downloading: {}",
        "log_saved": "✅ Saved: {} ({}%)",
        "log_no_download_link": "⚠️ No download link or image URL found on this page.",
        "log_network_error": "❌ Network error while downloading: {}",
        "log_http_error": "❌ Download failed: HTTP {}",
        "log_file_write_error": "❌ Error writing file: {}",
        "log_browser_error": "❌ Browser start error: {}",
        "log_page_error": "❌ Page load error: {}"
    },
    "Polski": {
        "title": "Metryki Downloader (Książka Jednostki na URL)",
        "url_placeholder": "Wprowadź główny URL (np. https://metryki.genealodzy.pl/id598-sy1904-kt1)",
        "add_button": "Dodaj",
        "folder_placeholder": "Wprowadź lub wybierz folder zapisu …",
        "folder_button": "Folder zapisu",
        "download_button": "Pobierz",
        "stop_button": "Stop",
        "reset_button": "Reset",
        "delete_button": "Usuń",
        "toggle_log_button": "Pokaż/ukryj log",
        "import_button": "Import Lista",
        "export_button": "Export Lista",
        "home_button": "🏠 Metryki Genealodzy",
        "progress_label": "Postęp pobierania:",
        "log_label": "Log:",
        "log_added": "➕ URL dodany: {}",
        "log_folder": "📂 Wybrano folder zapisu: {}",
        "log_reset": "🔄 Kolejka zresetowana.",
        "log_deleted": "❌ Usunięto: {}",
        "log_no_selection": "ℹ️ Brak zaznaczonych elementów do usunięcia.",
        "log_imported": "📥 Kolejka zaimportowana: {}",
        "log_exported": "📤 Kolejka wyeksportowana: {}",
        "log_error_import": "❌ Błąd podczas importu: {}",
        "log_error_export": "❌ Błąd podczas eksportu: {}",
        "log_download_started": "⬇️ Pobieranie rozpoczęte...",
        "log_download_running": "⚠️ Pobieranie już trwa.",
        "log_no_urls": "⚠️ Brak URL w kolejce!",
        "log_no_folder": "⚠️ Nie wybrano poprawnego folderu zapisu!",
        "log_download_finished": "🎉 Pobieranie zakończone.",
        "log_stop_requested": "⏹️ Stop żądany.",
        "log_no_download": "ℹ️ Brak trwającego pobierania do zatrzymania.",
        "log_open_main": "🌍 Otwieranie strony głównej: {}",
        "log_unit_folder": "📂 Folder jednostki: {}",
        "log_pages_found": "📄 {} stron/obrazów znaleziono.",
        "log_open_page": "[{}/{}] Otwieranie strony: {}",
        "log_downloading": "⬇️ Pobieranie: {}",
        "log_saved": "✅ Zapisano: {} ({}%)",
        "log_no_download_link": "⚠️ Brak linku do pobrania lub URL obrazu na tej stronie.",
        "log_network_error": "❌ Błąd sieci podczas pobierania: {}",
        "log_http_error": "❌ Błąd pobierania: HTTP {}",
        "log_file_write_error": "❌ Błąd zapisu pliku: {}",
        "log_browser_error": "❌ Błąd uruchomienia przeglądarki: {}",
        "log_page_error": "❌ Błąd ładowania strony: {}"
    }
}

current_lang = "Deutsch"

# ---------------- Helper Classes ----------------
class URLListWidget(QListWidget):
    """QListWidget mit Unterstützung für Entf-Taste (löschen der Auswahl)."""
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            parent = self.parent()
            if parent and hasattr(parent, "delete_selected"):
                parent.delete_selected()
        else:
            super().keyPressEvent(event)

# ---------------- DownloadWorker ----------------
class DownloadWorker(QThread):
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int, int)  # aktuelle, gesamt
    finished_signal = pyqtSignal()
    stopped = False

    def __init__(self, urls, save_folder):
        super().__init__()
        self.urls = urls
        self.save_folder = save_folder

    # ---------- Hilfsfunktionen ----------
    def sanitize_foldername(self, name: str) -> str:
        name = name.strip()
        if not name:
            return "Einheit_ohne_Name"
        allowed = " _-()[]0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        return "".join(c if c in allowed else "_" for c in name)

    def folder_name_from_url(self, url: str) -> str:
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            parts = []
            if "sy" in params:
                parts.append(f"sy{params['sy'][0]}")
            if "id" in params:
                parts.append(f"id{params['id'][0]}")
            if "kt" in params:
                parts.append(f"kt{params['kt'][0]}")
            if parts:
                return "Einheit_" + "_".join(parts)
            path_seg = os.path.basename(parsed.path) or "unit"
            return f"Einheit_{path_seg}"
        except Exception:
            return "Einheit_unbekannt"

    def try_extract_jednostka(self, driver) -> str:
        xpaths = [
            "//th[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'jednostka')]/following-sibling::td[1]",
            "//tr[th[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'jednostka')]]/td[1]",
            "//dt[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'jednostka')]/following-sibling::dd[1]",
            "//*[contains(translate(normalize-space(.),'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'),'jednostka')]"
        ]
        for xp in xpaths:
            try:
                elems = driver.find_elements(By.XPATH, xp)
                if not elems:
                    continue
                el = elems[0]
                text = el.text.strip()
                if not text:
                    try:
                        sib = el.find_element(By.XPATH, "following-sibling::*[1]")
                        text = sib.text.strip()
                    except Exception:
                        text = ""
                if not text:
                    continue
                lower = text.lower()
                if "jednostka" in lower:
                    candidate = text.split(":", 1)[1].strip() if ":" in text else text.replace("Jednostka", "").strip()
                else:
                    candidate = text
                if candidate:
                    return candidate[:200]
            except Exception:
                continue
        try:
            for tag in ("h1", "h2", "h3"):
                try:
                    el = driver.find_element(By.TAG_NAME, tag)
                    t = el.text.strip()
                    if t:
                        return t[:200]
                except Exception:
                    pass
            t = driver.title.strip()
            if t:
                return t[:200]
        except Exception:
            pass
        return ""

    def create_driver(self, chrome_options):
        try:
            from selenium.webdriver.chrome.service import Service
            try:
                from webdriver_manager.chrome import ChromeDriverManager
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
                return driver
            except Exception:
                return webdriver.Chrome(options=chrome_options)
        except Exception:
            return webdriver.Chrome(options=chrome_options)

    # ---------- Haupt-Thread ----------
    def run(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        try:
            driver = self.create_driver(chrome_options)
        except Exception as e:
            self.log_signal.emit(translations[current_lang]["log_browser_error"].format(e))
            self.finished_signal.emit()
            return

        total_files = 0
        try:
            for main_url in self.urls:
                try:
                    driver.get(main_url)
                    time.sleep(0.5)
                    link_elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='plik=']")
                    hrefs = list({a.get_attribute("href") for a in link_elements if a.get_attribute("href")})
                    total_files += len(hrefs)
                except Exception:
                    continue
        except Exception:
            total_files = 0

        current_file = 0

        try:
            for main_url in self.urls:
                if self.stopped:
                    self.log_signal.emit("⏹️ Download abgebrochen (Stop angefordert).")
                    break

                self.log_signal.emit(translations[current_lang]["log_open_main"].format(main_url))
                try:
                    driver.get(main_url)
                    time.sleep(1.2)
                except Exception as e:
                    self.log_signal.emit(translations[current_lang]["log_page_error"].format(e))
                    continue

                jednostka_text = self.try_extract_jednostka(driver)
                folder_name = self.sanitize_foldername(jednostka_text or self.folder_name_from_url(main_url))
                unit_folder = os.path.join(self.save_folder, folder_name)
                os.makedirs(unit_folder, exist_ok=True)
                self.log_signal.emit(translations[current_lang]["log_unit_folder"].format(unit_folder))

                try:
                    link_elements = driver.find_elements(By.CSS_SELECTOR, "a[href*='plik=']")
                    hrefs = []
                    seen = set()
                    for a in link_elements:
                        href = a.get_attribute("href")
                        if href and href not in seen:
                            seen.add(href)
                            hrefs.append(href)
                    page_urls = hrefs
                except Exception as e:
                    self.log_signal.emit(translations[current_lang]["log_page_error"].format(e))
                    page_urls = []

                self.log_signal.emit(translations[current_lang]["log_pages_found"].format(len(page_urls)))

                for idx, page_url in enumerate(page_urls, start=1):
                    if self.stopped:
                        self.log_signal.emit("⏹️ Download abgebrochen (Stop angefordert).")
                        break

                    self.log_signal.emit(translations[current_lang]["log_open_page"].format(idx, len(page_urls), page_url))
                    try:
                        driver.get(page_url)
                        time.sleep(0.6)
                    except Exception as e:
                        self.log_signal.emit(translations[current_lang]["log_page_error"].format(e))
                        continue

                    download_url = None
                    try:
                        candidates = driver.find_elements(By.CSS_SELECTOR, "a[href*='metryka_get.php?op=download'], a[href*='metryka_get.php'], a[href*='&plik=']")
                        for c in candidates:
                            href = c.get_attribute("href")
                            if href:
                                download_url = href
                                break
                    except Exception:
                        download_url = None

                    if not download_url:
                        try:
                            imgs = driver.find_elements(By.TAG_NAME, "img")
                            for im in imgs:
                                src = im.get_attribute("src")
                                if src and ("metbox" in src or src.lower().endswith((".jpg", ".jpeg", ".png", ".tif", ".tiff"))):
                                    download_url = src
                                    break
                        except Exception:
                            download_url = None

                    if not download_url:
                        self.log_signal.emit(translations[current_lang]["log_no_download_link"])
                        continue

                    self.log_signal.emit(translations[current_lang]["log_downloading"].format(download_url))
                    try:
                        r = requests.get(download_url, stream=True, timeout=30)
                    except Exception as e:
                        self.log_signal.emit(translations[current_lang]["log_network_error"].format(e))
                        continue

                    if r.status_code != 200:
                        self.log_signal.emit(translations[current_lang]["log_http_error"].format(r.status_code))
                        continue

                    parsed = urlparse(download_url)
                    qs = parse_qs(parsed.query)
                    filename = qs["plik"][-1] if "plik" in qs and qs["plik"] else os.path.basename(parsed.path) or f"seite_{idx:03d}.jpg"

                    filepath = os.path.join(unit_folder, filename)
                    if os.path.exists(filepath):
                        base, ext = os.path.splitext(filename)
                        counter = 1
                        while True:
                            newname = f"{base}_{counter}{ext}"
                            newpath = os.path.join(unit_folder, newname)
                            if not os.path.exists(newpath):
                                filepath = newpath
                                filename = newname
                                break
                            counter += 1

                    try:
                        with open(filepath, "wb") as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                if chunk:
                                    f.write(chunk)
                        current_file += 1
                        percent = int(current_file / total_files * 100) if total_files > 0 else 0
                        self.progress_signal.emit(current_file, total_files)
                        self.log_signal.emit(translations[current_lang]["log_saved"].format(os.path.join(folder_name, filename), percent))
                    except Exception as e:
                        self.log_signal.emit(translations[current_lang]["log_file_write_error"].format(e))
        finally:
            try:
                driver.quit()
            except Exception:
                pass
        self.finished_signal.emit()

# ---------------- DownloaderApp ----------------
class DownloaderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.save_folder = ""
        self.worker = None
        self.log_visible = True

        self.setWindowIcon(QIcon("feather_blue.png"))
        self.setWindowTitle(translations[current_lang]["title"])
        self.resize(920, 750)
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Sprachwahl
        lang_layout = QHBoxLayout()
        self.lang_buttons = {}
        for lang_code in ["Deutsch", "English", "Polski"]:
            btn = QPushButton(lang_code)
            btn.setCheckable(True)
            btn.setStyleSheet("""
                QPushButton {
                    border-radius: 15px;
                    border: 2px solid #007BFF;
                    min-width: 50px;
                    min-height: 30px;
                }
                QPushButton:checked {
                    background-color: #007BFF;
                    color: white;
                }
            """)
            btn.clicked.connect(lambda checked, lc=lang_code: self.set_language(lc))
            lang_layout.addWidget(btn)
            self.lang_buttons[lang_code] = btn
        self.layout.addLayout(lang_layout)
        self.lang_buttons[current_lang].setChecked(True)

        # Home Button
        home_btn = QPushButton(translations[current_lang]["home_button"])
        home_btn.setStyleSheet("background-color: #17a2b8; color: white; font-weight: bold;")
        home_btn.clicked.connect(lambda: webbrowser.open("https://metryki.genealodzy.pl/"))
        self.layout.addWidget(home_btn)

        # URL Eingabe
        url_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(translations[current_lang]["url_placeholder"])
        url_layout.addWidget(self.url_input)
        self.add_button = QPushButton(translations[current_lang]["add_button"])
        self.add_button.clicked.connect(self.add_url)
        url_layout.addWidget(self.add_button)
        self.layout.addLayout(url_layout)

        # URL Liste
        self.url_list = URLListWidget(self)
        self.url_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.layout.addWidget(self.url_list)

        # Ordner
        folder_layout = QHBoxLayout()
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText(translations[current_lang]["folder_placeholder"])
        folder_layout.addWidget(self.folder_input)
        self.folder_button = QPushButton(translations[current_lang]["folder_button"])
        self.folder_button.clicked.connect(self.choose_folder)
        folder_layout.addWidget(self.folder_button)
        self.layout.addLayout(folder_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        self.download_button = QPushButton(translations[current_lang]["download_button"])
        self.download_button.clicked.connect(self.start_download)
        btn_layout.addWidget(self.download_button)
        self.stop_button = QPushButton(translations[current_lang]["stop_button"])
        self.stop_button.clicked.connect(self.stop_download)
        btn_layout.addWidget(self.stop_button)
        self.reset_button = QPushButton(translations[current_lang]["reset_button"])
        self.reset_button.clicked.connect(self.reset_list)
        btn_layout.addWidget(self.reset_button)
        self.delete_button = QPushButton(translations[current_lang]["delete_button"])
        self.delete_button.clicked.connect(self.delete_selected)
        btn_layout.addWidget(self.delete_button)
        self.toggle_log_button = QPushButton(translations[current_lang]["toggle_log_button"])
        self.toggle_log_button.clicked.connect(self.toggle_log)
        btn_layout.addWidget(self.toggle_log_button)
        self.import_button = QPushButton(translations[current_lang]["import_button"])
        self.import_button.clicked.connect(self.import_list)
        btn_layout.addWidget(self.import_button)
        self.export_button = QPushButton(translations[current_lang]["export_button"])
        self.export_button.clicked.connect(self.export_list)
        btn_layout.addWidget(self.export_button)
        self.layout.addLayout(btn_layout)

        # Fortschritt
        self.progress_bar = QProgressBar()
        self.progress_label = QLabel(translations[current_lang]["progress_label"])
        self.layout.addWidget(self.progress_label)
        self.layout.addWidget(self.progress_bar)

        # Log
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        self.layout.addWidget(QLabel(translations[current_lang]["log_label"]))
        self.layout.addWidget(self.log_area)

    # ---------- Sprachwechsel ----------
    def set_language(self, lang_code):
        global current_lang
        current_lang = lang_code
        for code, btn in self.lang_buttons.items():
            btn.setChecked(code == lang_code)
        self.setWindowTitle(translations[current_lang]["title"])
        self.url_input.setPlaceholderText(translations[current_lang]["url_placeholder"])
        self.add_button.setText(translations[current_lang]["add_button"])
        self.folder_input.setPlaceholderText(translations[current_lang]["folder_placeholder"])
        self.folder_button.setText(translations[current_lang]["folder_button"])
        self.download_button.setText(translations[current_lang]["download_button"])
        self.stop_button.setText(translations[current_lang]["stop_button"])
        self.reset_button.setText(translations[current_lang]["reset_button"])
        self.delete_button.setText(translations[current_lang]["delete_button"])
        self.toggle_log_button.setText(translations[current_lang]["toggle_log_button"])
        self.import_button.setText(translations[current_lang]["import_button"])
        self.export_button.setText(translations[current_lang]["export_button"])
        self.progress_label.setText(translations[current_lang]["progress_label"])

    # ---------- Log ----------
    def log(self, message: str):
        if self.log_visible:
            self.log_area.append(message)
        print(message)

    # ---------- URL ----------
    def add_url(self):
        url = self.url_input.text().strip()
        if url:
            self.url_list.addItem(url)
            self.url_input.clear()
            self.log(translations[current_lang]["log_added"].format(url))

    # ---------- Ordner ----------
    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, translations[current_lang]["folder_button"])
        if folder:
            self.folder_input.setText(folder)
            self.save_folder = folder
            self.log(translations[current_lang]["log_folder"].format(folder))

    # ---------- Liste ----------
    def reset_list(self):
        self.url_list.clear()
        self.log(translations[current_lang]["log_reset"])

    def delete_selected(self):
        items = self.url_list.selectedItems()
        if not items:
            self.log(translations[current_lang]["log_no_selection"])
            return
        for it in items:
            row = self.url_list.row(it)
            url = it.text()
            self.url_list.takeItem(row)
            self.log(translations[current_lang]["log_deleted"].format(url))

    # ---------- Log ein/aus ----------
    def toggle_log(self):
        self.log_visible = not self.log_visible
        self.log_area.setVisible(self.log_visible)

    # ---------- Import/Export ----------
    def import_list(self):
        path, _ = QFileDialog.getOpenFileName(self, "Import", "", "Text files (*.txt)")
        if path:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            self.url_list.addItem(line)
                self.log(translations[current_lang]["log_imported"].format(path))
            except Exception as e:
                self.log(translations[current_lang]["log_error_import"].format(e))

    def export_list(self):
        path, _ = QFileDialog.getSaveFileName(self, "Export", "", "Text files (*.txt)")
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    for i in range(self.url_list.count()):
                        f.write(self.url_list.item(i).text() + "\n")
                self.log(translations[current_lang]["log_exported"].format(path))
            except Exception as e:
                self.log(translations[current_lang]["log_error_export"].format(e))

    # ---------- Download ----------
    def start_download(self):
        if self.worker and self.worker.isRunning():
            self.log(translations[current_lang]["log_download_running"])
            return
        urls = [self.url_list.item(i).text() for i in range(self.url_list.count())]
        if not urls:
            self.log(translations[current_lang]["log_no_urls"])
            return
        self.save_folder = self.folder_input.text().strip()
        if not self.save_folder or not os.path.isdir(self.save_folder):
            self.log(translations[current_lang]["log_no_folder"])
            return
        self.progress_bar.setValue(0)
        self.worker = DownloadWorker(urls, self.save_folder)
        self.worker.log_signal.connect(self.log)
        self.worker.progress_signal.connect(lambda c, t: self.progress_bar.setValue(int(c/t*100) if t>0 else 0))
        self.worker.finished_signal.connect(lambda: self.log(translations[current_lang]["log_download_finished"]))
        self.worker.start()
        self.log(translations[current_lang]["log_download_started"])

    def stop_download(self):
        if self.worker and self.worker.isRunning():
            self.worker.stopped = True
            self.log(translations[current_lang]["log_stop_requested"])
        else:
            self.log(translations[current_lang]["log_no_download"])

# ---------------- Main ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = DownloaderApp()
    window.show()
    sys.exit(app.exec())
