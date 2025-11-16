# MetrykiDownloader
A Downloader for Books and Pictures from Metryki.

![alt text](https://github.com/Testatost/Metryki-Downloader/blob/main/Metryki%20Downloader.png?raw=true)



🇩🇪 Deutsch
🔑 Hauptaufgabe

• Du kannst URLs von Büchern, Karten oder Dokumenten von metryki.genealodzy.pl eingeben.
• Das Programm sucht in der Seite nach IIP-Bildserver-Links (das sind die hochauflösenden Scans).
• Es baut daraus direkte Download-Links zu JPEG-Bildern.
• Diese Bilder werden als Einzelseiten (page_0001.jpg, page_0002.jpg, …) in einen Zielordner heruntergeladen.
• Mehrere Bücher können in eine Warteliste gelegt und nacheinander heruntergeladen werden.

🛠️ Funktionen
1. Sprachen

• Oberfläche in Deutsch 🇩🇪, Englisch 🇬🇧 und Polnisch 🇵🇱 umschaltbar.

2. Buchverwaltung

• URL + Zielordner + gewünschte Seiten angeben.
• Seiten können z. B. als 1,5,8-10 spezifiziert werden, leer = alle.
• Bücher können hinzugefügt, gelöscht oder die Seitenbereiche geändert werden.
• Wartelisten lassen sich als JSON speichern und wieder laden.

3. Download

• Bilder werden seitenweise geladen.
• Fortschritt je Buch (✅, ⚠️, ❌) und Gesamtfortschritt in einer Fortschrittsleiste angezeigt.
• Abbruch (Stop-Button) jederzeit möglich.
• Wiederaufnahme über gespeicherte Warteliste.

4. Logging

• Meldungen (z. B. „Buch hinzugefügt“, „Download gestartet“) werden im Logbereich angezeigt.
• Optional werden die Logs in einer Datei download_log.txt im Zielordner gespeichert.
• Logfenster kann ein-/ausgeblendet werden.

5. GUI-Details (Tkinter)

• Tabellenansicht der Warteliste mit URL, Seiten, Status.
• Buttons für „Download starten“, „Stoppen“, „Reset“.
• Kontextfunktionen wie Doppelklick → Buch-URL im Browser öffnen.
• Fortschrittsbalken für alle Bücher.

---------------------------------------------------------------------------------------------------

🇬🇧 English
🔑 Main Purpose

• You can enter URLs of books, maps, or documents from metryki.genealodzy.pl.
• The program scans the page for IIP image server links (these point to the high-resolution scans).
• It then builds direct JPEG download links.
• These images are saved as individual pages (page_0001.jpg, page_0002.jpg, …) in a chosen folder.
• Multiple books can be added to a waiting list and downloaded one after another.

🛠️ Features
1. Languages

• Interface available in German 🇩🇪, English 🇬🇧, and Polish 🇵🇱.

2. Book management

• Enter URL + target folder + desired pages.
• Pages can be specified like 1,5,8-10; empty = all pages.
• Books can be added, deleted, or edited (pages).
• Waiting lists can be saved as JSON and loaded later.

3. Download

• Downloads images page by page.
• Shows per-book status (✅, ⚠️, ❌) and overall progress bar.
• Can be stopped anytime.
• Downloads can be resumed from saved waiting lists.

4. Logging

• Messages (e.g., “Book added”, “Download started”) appear in the log window.
• Optionally saved to download_log.txt in the target folder.
• Log window can be shown/hidden.

5. GUI details (Tkinter)

• Table view of waiting list with URL, pages, and status.
• Buttons for “Download”, “Stop”, “Reset”.
• Double-click opens the book’s URL in browser.
• Global progress bar for all books.

---------------------------------------------------------------------------------------------------

🇵🇱 Polski
🔑 Główne zadanie

• Możesz wprowadzić adresy URL książek, map lub dokumentów z metryki.genealodzy.pl.
• Program wyszukuje na stronie linki do serwera obrazów IIP (to są skany w wysokiej rozdzielczości).
• Tworzy z nich bezpośrednie linki do pobrania plików JPEG.
• Obrazy są zapisywane jako pojedyncze strony (page_0001.jpg, page_0002.jpg, …) w wybranym folderze.
• Wiele książek można dodać do listy oczekujących i pobierać je kolejno.

🛠️ Funkcje
1. Języki

• Interfejs dostępny w języku niemieckim 🇩🇪, angielskim 🇬🇧 i polskim 🇵🇱.

2. Zarządzanie książkami

• Wprowadź URL + folder docelowy + żądane strony.
• Strony można określić np. 1,5,8-10; puste = wszystkie.
• Książki można dodawać, usuwać lub edytować zakres stron.
• Listy oczekujących można zapisać w formacie JSON i później wczytać.

3. Pobieranie

• Obrazy pobierane są strona po stronie.
• Pokazuje status każdej książki (✅, ⚠️, ❌) oraz pasek postępu całości.
• Pobieranie można zatrzymać w dowolnym momencie.
• Możliwe jest wznowienie pobierania z zapisanej listy oczekujących.

4. Logowanie

• Komunikaty (np. „Książka dodana”, „Pobieranie rozpoczęte”) wyświetlane są w oknie logów.
• Opcjonalnie zapisywane do pliku download_log.txt w folderze docelowym.
• Okno logów można pokazywać lub ukrywać.

5. Szczegóły GUI

• Widok tabeli listy oczekujących z kolumnami: URL, strony, status.
• Przyciski „Pobierz”, „Stop”, „Reset”.
• Podwójny klik otwiera URL książki w przeglądarce.
• Pasek postępu pokazuje postęp dla wszystkich książek.

--------------------------------------------------------------------------------------------

Disclaimer: This code as made with ChatGPT 5.
