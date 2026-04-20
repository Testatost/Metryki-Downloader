# Metryki Downloader

<p align="center">
  <img src="logo.png" alt="Metryki Downloader Logo" width="260"> <br>
</p>

Metryki Downloader is a desktop application for downloading scans from **metryki.genealodzy.pl**.

The current source code is based on **PyQt6** and is organized as a modular package in `metrykidownloader/`.

![Screenshot](splash.png)

## Overview

The application can:

- open URLs from `metryki.genealodzy.pl`
- detect scan/image links on the page
- generate direct JPEG download links
- download all pages or selected page ranges
- queue multiple entries in a waiting list
- save and load waiting lists as JSON
- export downloaded JPG folders to PDF
- show a live log and save the log manually to a text file
- switch between German, English, and Polish
- remember the selected language and theme

## Requirements

- Python 3.10+
- PyQt6
- requests
- selenium
- webdriver-manager
- Pillow

## Installation

### Windows / PyCharm / virtual environment

```bash
python -m pip install --upgrade pip
pip install PyQt6 requests selenium webdriver-manager Pillow
```

### Linux Mint / Ubuntu

```bash
sudo apt update
sudo apt install python3-pip
python3 -m pip install --upgrade pip
pip install PyQt6 requests selenium webdriver-manager Pillow
```

## Usage

1. Start the program.
2. Enter a Metryki URL.
3. Choose the target directory.
4. Optionally enter page ranges such as `1,5,8-10`.
5. Add one or more entries to the waiting list.
6. Start the download.

## Main features

### Download queue

- multiple books, maps, or documents can be added to a waiting list
- entries can be deleted again
- page ranges can be changed later
- double-click on a row opens the original URL in the browser

### Download logic

- the application searches the page for image/IIP-related links
- direct JPEG download URLs are generated automatically
- pages are downloaded one by one
- the overall progress is shown in a progress bar
- each queue item gets a status symbol: `⏳`, `✅`, `⚠️`, `❌`

### Folder naming

The current code creates folders based on extracted metadata and groups downloads into a readable structure.

```text
Target folder/
└── Place/
    └── TypeDE - TypePL - TypeEN (Years)/
        ├── TypeDE - TypePL - TypeEN_001.jpg
        ├── TypeDE - TypePL - TypeEN_002.jpg
        └── TypeDE - TypePL - TypeEN (Years).pdf
```

### PDF export

Downloaded JPG files can be converted into a PDF per folder.

### Logging

- messages are shown in the log window inside the application
- the log can be shown or hidden
- the log can be saved manually to a chosen `.txt` file

### Interface

- available languages: German, English, Polish
- selected language is stored with `QSettings`
- dark mode / light mode is available
- selected theme is stored with `QSettings`

## Source code structure

The source code is split into modules inside `metrykidownloader/`.

### Module summary

- `main.py` – application entry point
- `app_constants.py` – application name, settings keys, default headers, paths
- `i18n.py` – UI texts for all supported languages
- `main_window.py` – full GUI and user interactions
- `metadata_parser.py` – metadata extraction for Metryki pages
- `models.py` – data models such as `BookEntry`
- `network.py` – HTTP requests and binary download helpers
- `styles.py` – light and dark Qt stylesheets
- `text_utils.py` – helper functions for text and URL processing
- `worker.py` – threaded downloader logic

## Notes

- Page ranges can be entered in formats such as `1,2,5-9`.
- Waiting lists are stored as `.json`.
- The application uses Selenium to resolve scan pages and image links dynamically.

## Disclaimer

This project was created with support from ChatGPT 5.
