from __future__ import annotations

import os
import time

import requests
from PyQt6.QtCore import QThread, pyqtSignal
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from metrykidownloader.app_constants import DEFAULT_HEADERS
from metrykidownloader.i18n import LANG
from metrykidownloader.metadata_parser import parse_metryki_metadata
from metrykidownloader.models import BookEntry
from metrykidownloader.network import download_binary
from metrykidownloader.text_utils import unique_preserve_order


class DownloaderWorker(QThread):
    log_message = pyqtSignal(str)
    book_status = pyqtSignal(int, str)
    global_progress = pyqtSignal(float)
    finished_signal = pyqtSignal()

    def __init__(self, books: list[BookEntry], ui_lang: str = "de", parent=None):
        super().__init__(parent)
        self.books = books
        self.ui_lang = ui_lang
        self._stop_requested = False
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)

    def _t(self, key: str) -> str:
        lang = self.ui_lang if self.ui_lang in LANG else "de"
        return LANG[lang].get(key, LANG.get("en", {}).get(key, LANG["de"].get(key, key)))

    def stop(self) -> None:
        self._stop_requested = True

    def log(self, message: str) -> None:
        self.log_message.emit(message)

    def parse_pages(self, pages_str: str, total: int) -> list[int]:
        if not str(pages_str).strip():
            return list(range(1, total + 1))

        pages: list[int] = []
        for part in str(pages_str).split(","):
            part = part.strip()
            if not part:
                continue
            if "-" in part:
                try:
                    start_page, end_page = map(int, part.split("-", 1))
                    pages.extend(i for i in range(start_page, end_page + 1) if 1 <= i <= total)
                except Exception:
                    pass
            else:
                try:
                    page_number = int(part)
                    if 1 <= page_number <= total:
                        pages.append(page_number)
                except Exception:
                    pass

        return sorted(set(pages))

    def _create_driver(self):
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager

        options = Options()
        options.add_argument("--headless=new")
        options.add_argument("--disable-features=RendererCodeIntegrity")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")

        try:
            service = Service(ChromeDriverManager().install())
            return webdriver.Chrome(service=service, options=options)
        except Exception:
            return webdriver.Chrome(options=options)

    def _collect_links(self, driver, css_selector: str) -> list[str]:
        links: list[str] = []
        for element in driver.find_elements(By.CSS_SELECTOR, css_selector):
            href = element.get_attribute("href")
            if href:
                links.append(href)
        return unique_preserve_order(links)

    def _get_book_page_links(self, driver, url: str) -> list[str]:
        driver.get(url)
        time.sleep(0.8)
        return self._collect_links(driver, "a[href*='plik=']")

    def _get_download_url(self, driver, page_url: str) -> str | None:
        driver.get(page_url)
        time.sleep(0.5)
        links = self._collect_links(driver, "a[href*='plik=']")
        return links[0] if links else None

    def _extract_metadata(self, driver) -> dict:
        time.sleep(0.2)
        candidates: list[str] = []
        for element in driver.find_elements(By.XPATH, "//td[contains(., 'Zespół:')]"):
            text = element.text.strip()
            if text:
                candidates.append(text)

        if not candidates:
            page_text = driver.find_element(By.TAG_NAME, "body").text
            if "Zespół:" in page_text:
                start = page_text.index("Zespół:")
                snippet = page_text[start:start + 1200]
                candidates.append(snippet)

        return parse_metryki_metadata("\n".join(candidates))

    def _resolve_output_folder(self, book: BookEntry, metadata: dict) -> str:
        base_outdir = book.outdir or os.getcwd()
        place = metadata.get("place", "Unknown_place")
        type_de = metadata.get("type_de", "Unknown")
        type_pl = metadata.get("type_pl", "Unknown")
        type_en = metadata.get("type_en", "Unknown")
        years = metadata.get("years", "Unknown")

        folder_name = f"{type_de} - {type_pl} - {type_en} ({years})"
        outdir = os.path.join(base_outdir, place, folder_name)
        os.makedirs(outdir, exist_ok=True)
        return outdir

    def _count_total_requested_pages(self, driver) -> int:
        total = 0
        for book in self.books:
            if self._stop_requested:
                break
            try:
                page_links = self._get_book_page_links(driver, book.url)
                total += len(self.parse_pages(book.pages, len(page_links)))
            except Exception:
                self.log(self._t("worker_load_error").format(url=book.url, error="count failed"))
        return total

    def run(self) -> None:
        try:
            driver = self._create_driver()
        except Exception as exc:
            self.log(f"[!] {self._t('worker_browser_error').format(error=exc)}")
            self.finished_signal.emit()
            return

        files_done = 0

        try:
            total_files = self._count_total_requested_pages(driver)

            for row, book in enumerate(self.books):
                if self._stop_requested:
                    self.log(self._t("worker_cancelled"))
                    self.book_status.emit(row, "❌")
                    break

                try:
                    self.log(f"[🌍] {self._t('worker_opening').format(url=book.url)}")
                    page_links = self._get_book_page_links(driver, book.url)
                    if not page_links:
                        self.log(self._t("worker_no_pages").format(url=book.url))
                        self.book_status.emit(row, "⚠️")
                        continue

                    metadata = self._extract_metadata(driver)
                    outdir = self._resolve_output_folder(book, metadata)
                    self.log(f"[📂] {self._t('worker_folder').format(path=outdir)}")

                    selected_page_numbers = self.parse_pages(book.pages, len(page_links))
                    if not selected_page_numbers:
                        self.log(f"[!] {self._t('worker_invalid_pages').format(url=book.url, pages=book.pages)}")
                        self.book_status.emit(row, "⚠️")
                        continue

                    errors = 0
                    type_de = metadata.get("type_de", "Unknown")
                    type_pl = metadata.get("type_pl", "Unknown")
                    type_en = metadata.get("type_en", "Unknown")

                    for logical_index, page_number in enumerate(selected_page_numbers, start=1):
                        if self._stop_requested:
                            errors += 1
                            break

                        page_url = page_links[page_number - 1]
                        download_url = self._get_download_url(driver, page_url)
                        if not download_url:
                            self.log(f"[!] {self._t('worker_no_download_url').format(page=page_number, url=page_url)}")
                            errors += 1
                            continue

                        filename = f"{type_de} - {type_pl} - {type_en}_{logical_index:03d}.jpg"
                        filepath = os.path.join(outdir, filename)

                        try:
                            self.log(f"[💾] {self._t('worker_downloading').format(name=filename, path=filepath)}")
                            download_binary(download_url, filepath, self.session)
                            files_done += 1
                            progress = (files_done / total_files) * 100 if total_files else 0
                            self.global_progress.emit(progress)
                        except Exception as exc:
                            errors += 1
                            self.log(f"[!] {self._t('worker_download_error').format(page=page_number, error=exc)}")

                    if errors == 0:
                        self.book_status.emit(row, "✅")
                    elif errors < len(selected_page_numbers):
                        self.book_status.emit(row, "⚠️")
                    else:
                        self.book_status.emit(row, "❌")

                except Exception as exc:
                    self.log(f"[!] {self._t('worker_load_error').format(url=book.url, error=exc)}")
                    self.book_status.emit(row, "❌")

        finally:
            try:
                driver.quit()
            except Exception:
                pass
            self.log(self._t("worker_all_done"))
            self.finished_signal.emit()
