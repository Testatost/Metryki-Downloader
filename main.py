import sys
import os
import time
import webbrowser
import requests
import re
import json
from PIL import Image

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit,
    QFileDialog, QLineEdit, QListWidget, QListWidgetItem,
    QAbstractItemView, QProgressBar
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt
from PyQt6.QtGui import QIcon

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


# ---------------- Übersetzungen ----------------
translations = {
    "Deutsch": {
        "title": "Metryki Downloader",
        "url_placeholder": "Haupt-URL eingeben …",
        "add_button": "Hinzufügen",
        "folder_placeholder": "Zielordner eingeben oder wählen …",
        "folder_button": "Zielordner",
        "page_placeholder": "z.B. 1, 5-9, leer = alle Seiten",
        "download_button": "Download",
        "stop_button": "Stopp",
        "reset_button": "Zurücksetzen",
        "delete_button": "Löschen",
        "home_button": "🏠 Metryki Genealodzy",
        "progress_label": "Fortschritt:",
        "log_added": "➕ URL hinzugefügt: {} | Seiten: {}",
        "log_folder": "📂 Zielordner gewählt: {}",
        "log_reset": "🔄 Warteliste zurückgesetzt.",
        "log_deleted": "❌ Gelöscht: {}",
        "log_no_urls": "⚠️ Keine URLs!",
        "log_no_folder": "⚠️ Kein gültiger Zielordner!",
        "log_download_started": "⬇️ Download gestartet...",
        "log_download_running": "⚠️ Läuft bereits!",
        "log_download_finished": "🎉 Fertig!",
        "export_button": "Liste exportieren",
        "import_button": "Liste importieren",
        "pdf_button": "PDFs pro Ordner speichern",
    },

    "English": {
        "title": "Metryki Downloader",
        "url_placeholder": "Enter main URL …",
        "add_button": "Add",
        "folder_placeholder": "Select a target folder…",
        "folder_button": "Target folder",
        "page_placeholder": "e.g. 1, 5-9, empty = all pages",
        "download_button": "Download",
        "stop_button": "Stop",
        "reset_button": "Reset",
        "delete_button": "Delete",
        "home_button": "🏠 Metryki Genealodzy",
        "progress_label": "Progress:",
        "log_added": "➕ URL added: {} | Pages: {}",
        "log_folder": "📂 Folder selected: {}",
        "log_reset": "🔄 List cleared.",
        "log_deleted": "❌ Deleted: {}",
        "log_no_urls": "⚠️ No URLs!",
        "log_no_folder": "⚠️ Invalid folder!",
        "log_download_started": "⬇️ Download started...",
        "log_download_running": "⚠️ Already running!",
        "log_download_finished": "🎉 Done!",
        "export_button": "Export list",
        "import_button": "Import list",
        "pdf_button": "Save PDFs per folder",
    },

    "Polski": {
        "title": "Metryki Downloader",
        "url_placeholder": "Wprowadź główny adres URL …",
        "add_button": "Dodaj",
        "folder_placeholder": "Wybierz folder docelowy …",
        "folder_button": "Folder docelowy",
        "page_placeholder": "np. 1, 5-9, puste = wszystkie strony",
        "download_button": "Pobierz",
        "stop_button": "Stop",
        "reset_button": "Reset",
        "delete_button": "Usuń",
        "home_button": "🏠 Metryki Genealodzy",
        "progress_label": "Postęp:",
        "log_added": "➕ Dodano URL: {} | Strony: {}",
        "log_folder": "📂 Wybrano folder: {}",
        "log_reset": "🔄 Wyczyść listę.",
        "log_deleted": "❌ Usunięto: {}",
        "log_no_urls": "⚠️ Brak URL!",
        "log_no_folder": "⚠️ Nieprawidłowy folder!",
        "log_download_started": "⬇️ Rozpoczęto pobieranie...",
        "log_download_running": "⚠️ Już trwa!",
        "log_download_finished": "🎉 Gotowe!",
        "export_button": "Eksportuj listę",
        "import_button": "Importuj listę",
        "pdf_button": "Zapisz PDF-y w folderach",
    }
}

current_lang = "Deutsch"


# ---------------- URL-Liste ----------------
class URLListWidget(QListWidget):
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Delete:
            parent = self.parent()
            if parent and hasattr(parent, "delete_selected"):
                parent.delete_selected()
        else:
            super().keyPressEvent(event)


# ---------------- Downloader Thread ----------------
class DownloadWorker(QThread):
    log_signal = pyqtSignal(str)
    progress_signal = pyqtSignal(int, int)
    finished_signal = pyqtSignal()
    stopped = False

    POLISH_TO_GERMAN = {
        "Urodzenia": "Geburten",
        "Małżeństwa": "Heiraten",
        "Zgony": "Sterbefälle",
    }

    POLISH_TO_ENGLISH = {
        "Urodzenia": "Births",
        "Małżeństwa": "Marriages",
        "Zgony": "Deaths"
    }

    def __init__(self, entries, save_folder):
        super().__init__()
        self.entries = entries
        self.save_folder = save_folder

    def sanitize(self, name: str) -> str:
        name = name.strip()
        allowed = " _-()[]0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        return "".join(c if c in allowed else "_" for c in name)

    def parse_page_selection(self, text, total):
        if not text:
            return list(range(1, total + 1))
        pages = set()
        parts = [p.strip() for p in text.split(",") if p.strip()]
        for part in parts:
            if "-" in part:
                x, y = part.split("-", 1)
                if x.isdigit() and y.isdigit():
                    pages.update(range(int(x), int(y) + 1))
            elif part.isdigit():
                pages.add(int(part))
        return sorted(i for i in pages if 1 <= i <= total)

    def create_driver(self, chrome_options):
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        chrome_options.add_argument("--disable-features=RendererCodeIntegrity")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        try:
            service = Service(ChromeDriverManager().install())
            return webdriver.Chrome(service=service, options=chrome_options)
        except:
            return webdriver.Chrome(options=chrome_options)

    def extract_metadata(self, driver):
        time.sleep(0.3)
        try:
            block = driver.find_element(By.XPATH, "//td[contains(., 'Zespół:')]")
            text = block.text
        except:
            return ("Unknown_place", "Unknown", "Unknown")

        ort = "Unknown_place"
        buch_pl = "Unknown"
        jahr = "Unknown"
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        for i, line in enumerate(lines):
            if "Zespół" in line:
                candidate = line
                if "/" not in candidate and i + 1 < len(lines):
                    candidate = lines[i + 1]
                if "/" in candidate:
                    after_slash = candidate.split("/", 1)[1].strip()
                else:
                    after_slash = candidate
                m = re.search(r"miasta\s+(.+)", after_slash)
                if m:
                    place = m.group(1).strip()
                else:
                    m2 = re.search(r"Urząd\s+Stanu\s+Cywilnego\s+(.+?)(?:\s*\(|$)", after_slash)
                    if m2:
                        place = m2.group(1).strip()
                    else:
                        main = after_slash.split("(", 1)[0].strip()
                        tokens = main.split()
                        place = tokens[-1] if tokens else "Unknown_place"
                ort = self.sanitize(place)
            elif line.startswith("Katalog:"):
                buch_pl = line.split(":", 1)[1].strip()
            elif line.startswith("Lata:"):
                jahr = line.split(":", 1)[1].strip()
        return (
            ort,
            self.sanitize(buch_pl),
            self.sanitize(jahr),
        )

    def run(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        try:
            driver = self.create_driver(chrome_options)
        except Exception as e:
            self.log_signal.emit(f"❌ Browserfehler: {e}")
            self.finished_signal.emit()
            return

        total_files = 0
        for url, pagesel in self.entries:
            try:
                driver.get(url)
                time.sleep(0.5)
                links = driver.find_elements(By.CSS_SELECTOR, "a[href*='plik=']")
                total_files += len({l.get_attribute("href") for l in links})
            except:
                pass

        current_file = 0
        for url, pagesel in self.entries:
            if self.stopped:
                break

            self.log_signal.emit(f"🌍 Öffne: {url}")
            driver.get(url)
            time.sleep(1)

            ort, buch_pl, jahr = self.extract_metadata(driver)
            buch_de = self.POLISH_TO_GERMAN.get(buch_pl, buch_pl)
            buch_en = self.POLISH_TO_ENGLISH.get(buch_pl, buch_pl)

            unit_folder = os.path.join(
                self.save_folder,
                ort,
                f"{buch_de} - {buch_pl} - {buch_en} ({jahr})"
            )
            os.makedirs(unit_folder, exist_ok=True)

            self.log_signal.emit(f"📂 Ordner: {unit_folder}")

            links = driver.find_elements(By.CSS_SELECTOR, "a[href*='plik=']")
            all_pages = list({l.get_attribute("href") for l in links})

            valid_numbers = self.parse_page_selection(pagesel, len(all_pages))
            pages = [p for i, p in enumerate(all_pages, 1) if i in valid_numbers]

            for idx, page_url in enumerate(pages, 1):
                if self.stopped:
                    break

                driver.get(page_url)
                time.sleep(0.6)

                download_url = None
                for c in driver.find_elements(By.CSS_SELECTOR, "a[href*='plik=']"):
                    href = c.get_attribute("href")
                    if href:
                        download_url = href
                        break

                if not download_url:
                    continue

                try:
                    r = requests.get(download_url, stream=True, timeout=20)
                except:
                    continue

                if r.status_code != 200:
                    continue

                filename = f"{buch_de} - {buch_pl} - {buch_en}_{idx:03d}.jpg"
                filepath = os.path.join(unit_folder, filename)

                with open(filepath, "wb") as f:
                    for chunk in r.iter_content(8192):
                        f.write(chunk)

                current_file += 1
                percent = int(current_file / total_files * 100) if total_files else 0
                self.progress_signal.emit(current_file, total_files)
                self.log_signal.emit(f"💾 {filename} ({percent}%) gespeichert")

        try:
            driver.quit()
        except:
            pass

        self.finished_signal.emit()


# ---------------- GUI ----------------
class DownloaderApp(QWidget):
    def __init__(self):
        super().__init__()
        self.worker = None
        self.save_folder = ""
        self.setWindowIcon(QIcon("feather_blue.png"))
        self.resize(950, 770)
        self.setWindowTitle(translations[current_lang]["title"])
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # ---------------- Row 1: Home (links) | Sprachen (rechts)
        row1 = QHBoxLayout()

        self.home = QPushButton(translations[current_lang]["home_button"])
        self.home.setFixedWidth(180)
        self.home.setStyleSheet("background-color: #4a90e2; color: white;")
        self.home.clicked.connect(lambda: webbrowser.open("https://metryki.genealodzy.pl/"))
        row1.addWidget(self.home, alignment=Qt.AlignmentFlag.AlignLeft)

        lang_layout = QHBoxLayout()
        lang_layout.setSpacing(5)

        self.lang_buttons = {}
        for lang in ["Deutsch", "English", "Polski"]:
            btn = QPushButton(lang)
            btn.setCheckable(True)
            btn.setFixedWidth(80)
            btn.setChecked(lang == current_lang)
            btn.setStyleSheet("background-color: #777; color: white;")
            btn.clicked.connect(lambda checked, lc=lang: self.set_language(lc))
            lang_layout.addWidget(btn)
            self.lang_buttons[lang] = btn

        row1.addLayout(lang_layout)
        row1.setAlignment(lang_layout, Qt.AlignmentFlag.AlignRight)

        self.layout.addLayout(row1)

        # ---------------- Row 2: URL input
        url_row = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText(translations[current_lang]["url_placeholder"])
        url_row.addWidget(self.url_input)
        self.layout.addLayout(url_row)

        # ---------------- Row 3: Folder
        folder_row = QHBoxLayout()
        self.folder_input = QLineEdit()
        self.folder_input.setPlaceholderText(translations[current_lang]["folder_placeholder"])
        folder_row.addWidget(self.folder_input)

        self.folder_btn = QPushButton(translations[current_lang]["folder_button"])
        self.folder_btn.setFixedWidth(120)
        self.folder_btn.setStyleSheet("background-color: #9b9b9b; color: white;")
        self.folder_btn.clicked.connect(self.choose_folder)
        folder_row.addWidget(self.folder_btn)

        self.layout.addLayout(folder_row)

        # ---------------- Row 4: Page selector + Add button now here
        page_row = QHBoxLayout()

        self.page_input = QLineEdit()
        self.page_input.setPlaceholderText(translations[current_lang]["page_placeholder"])
        self.page_input.setFixedWidth(250)
        page_row.addWidget(self.page_input)

        self.add_btn = QPushButton(translations[current_lang]["add_button"])
        self.add_btn.setFixedWidth(140)
        self.add_btn.setStyleSheet("background-color: #4a90e2; color: white;")
        self.add_btn.clicked.connect(self.add_url)
        page_row.addWidget(self.add_btn)

        page_row.addStretch()
        self.layout.addLayout(page_row)

        # ---------------- Row 5: main actions
        btn_row1 = QHBoxLayout()

        self.dl_btn = QPushButton(translations[current_lang]["download_button"])
        self.dl_btn.setFixedWidth(130)
        self.dl_btn.setStyleSheet("background-color: #4a90e2; color: white;")

        self.stop_btn = QPushButton(translations[current_lang]["stop_button"])
        self.stop_btn.setFixedWidth(130)
        self.stop_btn.setStyleSheet("background-color: #f5a623; color: black;")

        self.reset_btn = QPushButton(translations[current_lang]["reset_button"])
        self.reset_btn.setFixedWidth(130)
        self.reset_btn.setStyleSheet("background-color: #a81060; color: white;")

        self.delete_btn = QPushButton(translations[current_lang]["delete_button"])
        self.delete_btn.setFixedWidth(130)
        self.delete_btn.setStyleSheet("background-color: #d0021b; color: white;")

        self.dl_btn.clicked.connect(self.start_download)
        self.stop_btn.clicked.connect(self.stop_download)
        self.reset_btn.clicked.connect(self.reset_list)
        self.delete_btn.clicked.connect(self.delete_selected)

        btn_row1.addWidget(self.dl_btn)
        btn_row1.addWidget(self.stop_btn)
        btn_row1.addWidget(self.reset_btn)
        btn_row1.addWidget(self.delete_btn)
        self.layout.addLayout(btn_row1)

        # ---------------- Row 6: export / import / PDF
        btn_row2 = QHBoxLayout()

        self.export_btn = QPushButton(translations[current_lang]["export_button"])
        self.export_btn.setFixedWidth(180)
        self.export_btn.setStyleSheet("background-color: #9b9b9b; color: white;")

        self.import_btn = QPushButton(translations[current_lang]["import_button"])
        self.import_btn.setFixedWidth(180)
        self.import_btn.setStyleSheet("background-color: #9b9b9b; color: white;")

        self.pdf_btn = QPushButton(translations[current_lang]["pdf_button"])
        self.pdf_btn.setFixedWidth(180)
        self.pdf_btn.setStyleSheet("background-color: #7ed321; color: black;")

        self.export_btn.clicked.connect(self.export_list)
        self.import_btn.clicked.connect(self.import_list)
        self.pdf_btn.clicked.connect(self.save_as_pdf)

        btn_row2.addWidget(self.export_btn)
        btn_row2.addWidget(self.import_btn)
        btn_row2.addWidget(self.pdf_btn)
        self.layout.addLayout(btn_row2)

        # ---------------- URL List
        self.url_list = URLListWidget(self)
        self.url_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.layout.addWidget(self.url_list)

        # ---------------- Progress bar
        self.progress = QProgressBar()
        self.layout.addWidget(self.progress)

        # ---------------- Log
        self.log_area = QTextEdit()
        self.layout.addWidget(self.log_area)

    #
    # ---- Restliche Methoden UNVERÄNDERT ----
    #

    def set_language(self, lang):
        global current_lang
        current_lang = lang

        for code, btn in self.lang_buttons.items():
            btn.setChecked(code == lang)

        self.setWindowTitle(translations[current_lang]["title"])
        self.url_input.setPlaceholderText(translations[current_lang]["url_placeholder"])
        self.folder_input.setPlaceholderText(translations[current_lang]["folder_placeholder"])
        self.page_input.setPlaceholderText(translations[current_lang]["page_placeholder"])

        self.home.setText(translations[current_lang]["home_button"])
        self.add_btn.setText(translations[current_lang]["add_button"])
        self.folder_btn.setText(translations[current_lang]["folder_button"])
        self.dl_btn.setText(translations[current_lang]["download_button"])
        self.stop_btn.setText(translations[current_lang]["stop_button"])
        self.reset_btn.setText(translations[current_lang]["reset_button"])
        self.delete_btn.setText(translations[current_lang]["delete_button"])
        self.export_btn.setText(translations[current_lang]["export_button"])
        self.import_btn.setText(translations[current_lang]["import_button"])
        self.pdf_btn.setText(translations[current_lang]["pdf_button"])

    def log(self, msg):
        self.log_area.append(msg)
        print(msg)

    def add_url(self):
        url = self.url_input.text().strip()
        pages = self.page_input.text().strip()
        if url:
            item = QListWidgetItem(f"{url} | {pages if pages else 'ALL'}")
            item.setData(Qt.ItemDataRole.UserRole, (url, pages))
            self.url_list.addItem(item)
            self.url_input.clear()
            self.page_input.clear()
            self.log(translations[current_lang]["log_added"].format(url, pages if pages else "ALL"))

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, translations[current_lang]["folder_button"])
        if folder:
            self.folder_input.setText(folder)
            self.save_folder = folder
            self.log(translations[current_lang]["log_folder"].format(folder))

    def reset_list(self):
        self.url_list.clear()
        self.log(translations[current_lang]["log_reset"])

    def delete_selected(self):
        for item in self.url_list.selectedItems():
            self.url_list.takeItem(self.url_list.row(item))
            self.log(translations[current_lang]["log_deleted"].format(item.text()))

    def start_download(self):
        if self.worker and self.worker.isRunning():
            self.log(translations[current_lang]["log_download_running"])
            return

        entries = []
        for i in range(self.url_list.count()):
            url, pages = self.url_list.item(i).data(Qt.ItemDataRole.UserRole)
            entries.append((url, pages))

        if not entries:
            self.log(translations[current_lang]["log_no_urls"])
            return

        folder = self.folder_input.text().strip()
        if not os.path.isdir(folder):
            self.log(translations[current_lang]["log_no_folder"])
            return

        self.progress.setValue(0)
        self.worker = DownloadWorker(entries, folder)

        self.worker.log_signal.connect(self.log)
        self.worker.progress_signal.connect(
            lambda c, t: self.progress.setValue(int(c / t * 100)) if t else self.progress.setValue(0)
        )
        self.worker.finished_signal.connect(
            lambda: self.log(translations[current_lang]["log_download_finished"])
        )

        self.worker.start()
        self.log(translations[current_lang]["log_download_started"])

    def stop_download(self):
        if self.worker and self.worker.isRunning():
            self.worker.stopped = True

    def export_list(self):
        if self.url_list.count() == 0:
            self.log("⚠️ Nichts zu exportieren.")
            return

        path, _ = QFileDialog.getSaveFileName(
            self, "JSON speichern", "", "JSON (*.json)"
        )
        if not path:
            return

        data = []
        for i in range(self.url_list.count()):
            url, pages = self.url_list.item(i).data(Qt.ItemDataRole.UserRole)
            data.append({"url": url, "pages": pages})

        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        self.log(f"💾 gespeichert: {path}")

    def import_list(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "JSON importieren", "", "JSON (*.json)"
        )
        if not path:
            return

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.url_list.clear()
            for entry in data:
                url = entry["url"]
                pages = entry.get("pages", "")
                item = QListWidgetItem(f"{url} | {pages if pages else 'ALL'}")
                item.setData(Qt.ItemDataRole.UserRole, (url, pages))
                self.url_list.addItem(item)

            self.log(f"📥 importiert: {path}")

        except Exception as e:
            self.log(f"❌ Fehler beim Import: {e}")

    def save_as_pdf(self):
        if not self.save_folder or not os.path.isdir(self.save_folder):
            self.log("⚠️ Kein gültiger Speicherordner!")
            return

        pdf_count = 0

        for root, dirs, _ in os.walk(self.save_folder):
            for d in dirs:
                dpath = os.path.join(root, d)
                jpg_files = [
                    os.path.join(dpath, f)
                    for f in os.listdir(dpath)
                    if f.lower().endswith(".jpg")
                ]
                if not jpg_files:
                    continue

                jpg_files.sort()

                images = []
                for file in jpg_files:
                    try:
                        img = Image.open(file).convert("RGB")
                        images.append(img)
                    except:
                        pass

                if not images:
                    continue

                pdf_path = os.path.join(dpath, f"{d}.pdf")

                try:
                    images[0].save(pdf_path, save_all=True, append_images=images[1:])
                    pdf_count += 1
                except Exception as e:
                    self.log(f"❌ PDF Fehler: {e}")

        self.log(f"📄 PDFs erstellt: {pdf_count}")


# ---------------- MAIN ----------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = DownloaderApp()
    w.show()
    sys.exit(app.exec())
