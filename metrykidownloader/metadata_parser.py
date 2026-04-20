from __future__ import annotations

import re

from metrykidownloader.text_utils import sanitize_name

POLISH_TO_GERMAN = {
    "Urodzenia": "Geburten",
    "Małżeństwa": "Heiraten",
    "Zgony": "Sterbefälle",
}

POLISH_TO_ENGLISH = {
    "Urodzenia": "Births",
    "Małżeństwa": "Marriages",
    "Zgony": "Deaths",
}


def _extract_place(source_line: str) -> str:
    text = source_line.strip()
    if "/" in text:
        text = text.split("/", 1)[1].strip()

    match = re.search(r"miasta\s+(.+)", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    match = re.search(r"Urząd\s+Stanu\s+Cywilnego\s+(.+?)(?:\s*\(|$)", text, re.IGNORECASE)
    if match:
        return match.group(1).strip()

    text = text.split("(", 1)[0].strip()
    tokens = text.split()
    return tokens[-1] if tokens else "Unknown_place"


def parse_metryki_metadata(raw_text: str) -> dict:
    lines = [line.strip() for line in str(raw_text or "").splitlines() if line.strip()]

    place = "Unknown_place"
    book_type_pl = "Unknown"
    year_label = "Unknown"

    for index, line in enumerate(lines):
        if "Zespół" in line:
            candidate = line
            if "/" not in candidate and index + 1 < len(lines):
                candidate = lines[index + 1]
            place = _extract_place(candidate)
        elif line.startswith("Katalog:"):
            book_type_pl = line.split(":", 1)[1].strip() or "Unknown"
        elif line.startswith("Lata:"):
            year_label = line.split(":", 1)[1].strip() or "Unknown"

    return {
        "place": sanitize_name(place, "Unknown_place"),
        "type_pl": sanitize_name(book_type_pl, "Unknown"),
        "type_de": sanitize_name(POLISH_TO_GERMAN.get(book_type_pl, book_type_pl), "Unknown"),
        "type_en": sanitize_name(POLISH_TO_ENGLISH.get(book_type_pl, book_type_pl), "Unknown"),
        "years": sanitize_name(year_label, "Unknown"),
    }
