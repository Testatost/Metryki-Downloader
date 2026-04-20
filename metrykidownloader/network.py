from __future__ import annotations

import requests


def download_binary(url: str, destination: str, session: requests.Session, timeout: int = 60) -> bool:
    response = session.get(url, stream=True, timeout=timeout)
    response.raise_for_status()
    with open(destination, "wb") as handle:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                handle.write(chunk)
    return True
