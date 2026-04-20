from __future__ import annotations

import re


INVALID_FS_CHARS = re.compile(r'[\\/:*?"<>|]')
WHITESPACE_RE = re.compile(r"\s+")


def sanitize_name(name: str, fallback: str = "Unknown") -> str:
    value = str(name or "").strip()
    value = INVALID_FS_CHARS.sub("_", value)
    value = WHITESPACE_RE.sub(" ", value)
    value = value.replace(" ", "_")
    value = value.strip("._")
    if len(value) > 140:
        value = value[:140].rstrip("._")
    return value or fallback


def unique_preserve_order(items: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        value = str(item or "").strip()
        if not value or value in seen:
            continue
        result.append(value)
        seen.add(value)
    return result
