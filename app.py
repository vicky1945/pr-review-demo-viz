import os
from urllib.parse import urlparse

import requests

API_KEY = os.environ.get("API_KEY")
if not API_KEY:
    raise RuntimeError("API_KEY environment variable is required")

ALLOWED_FETCH_HOSTS = frozenset({"api.example.com"})

def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("division by zero")
    return a / b

def _is_safe_url(url: str) -> bool:
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False
    if not parsed.hostname:
        return False
    if parsed.hostname in ("localhost", "127.0.0.1", "0.0.0.0"):
        return False
    return parsed.hostname in ALLOWED_FETCH_HOSTS

def fetch(url: str, timeout: float = 5.0) -> dict:
    if not _is_safe_url(url):
        raise ValueError(f"URL not allowed: {url}")

    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    return response.json()
