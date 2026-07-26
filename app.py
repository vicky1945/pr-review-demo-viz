import os
from typing import Any
from urllib.parse import urlparse

import requests

DEFAULT_ALLOWED_HOSTS = ("api.example.com",)


def get_api_key() -> str:
    key = os.environ.get("API_KEY")
    if not key:
        raise RuntimeError("API_KEY environment variable is required")
    return key


def allowed_fetch_hosts() -> frozenset[str]:
    raw = os.environ.get("ALLOWED_FETCH_HOSTS", ",".join(DEFAULT_ALLOWED_HOSTS))
    return frozenset(h.strip() for h in raw.split(",") if h.strip())


def divide(a: float, b: float) -> float:
    if b == 0:
        raise ValueError("division by zero")
    return a / b


def is_safe_url(url: str, allowed_hosts: frozenset[str] | None = None) -> bool:
    hosts = allowed_hosts if allowed_hosts is not None else allowed_fetch_hosts()
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        return False
    hostname = parsed.hostname
    if not hostname:
        return False
    if hostname in ("localhost", "127.0.0.1", "0.0.0.0"):
        return False
    return hostname in hosts


def fetch(url: str, timeout: float = 5.0, allowed_hosts: frozenset[str] | None = None) -> dict:
    """Fetch JSON from an allowlisted URL.

    Args:
        url: The URL to fetch from.
        timeout: Request timeout in seconds. Defaults to 5.0.
        allowed_hosts: Frozenset of allowed hostnames. Defaults to allowed_fetch_hosts().

    Returns:
        A dictionary parsed from the JSON response.

    Raises:
        ValueError: If the URL is not in the allowlist or response is not valid JSON object.
        requests.exceptions.RequestException: On network or HTTP errors.
    """
    if not is_safe_url(url, allowed_hosts=allowed_hosts):
        raise ValueError(f"URL not allowed: {url}")

    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    data = response.json()
    
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object from {url}, got {type(data).__name__}")
    
    return data
