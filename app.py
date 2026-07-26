import ipaddress
from urllib.parse import urlparse

import requests


ALLOWED_HOSTS = {"api.example.com"}


def divide(a: float, b: float) -> float:
    """Divide a by b.

    Raises:
        ValueError: If b is zero.
    """
    if b == 0:
        raise ValueError("division by zero")
    return a / b


def is_safe_url(url: str, allowed_hosts: set[str] = ALLOWED_HOSTS) -> bool:
    """Check if a URL is safe to fetch from (allowlist validation).

    Allowed hosts: api.example.com (configurable)
    Must use http or https scheme.
    Blocks all loopback and localhost addresses (127.0.0.0/8, ::1, etc).
    """
    try:
        parsed = urlparse(url)
    except Exception:
        return False

    # Check scheme
    if parsed.scheme not in ("http", "https"):
        return False

    # Check hostname
    hostname = parsed.hostname
    if not hostname:
        return False

    # Block loopback/localhost addresses using ipaddress module
    try:
        ip = ipaddress.ip_address(hostname)
        if ip.is_loopback or ip.is_unspecified:
            return False
    except ValueError:
        # Not an IP literal; check if it's the string "localhost"
        if hostname.lower() == "localhost":
            return False

    # Check allowlist
    return hostname in allowed_hosts


def fetch(url: str, timeout: float = 5.0) -> dict:
    """Fetch JSON from an allowlisted URL.

    Args:
        url: The URL to fetch from (must be in allowlist).
        timeout: Request timeout in seconds.

    Returns:
        The JSON response as a dict.

    Raises:
        ValueError: If URL is not allowed or response is not a JSON dict.
        requests.exceptions.RequestException: On network/HTTP errors.
        requests.exceptions.JSONDecodeError: If response body is not valid JSON.
    """
    if not is_safe_url(url):
        raise ValueError(f"URL not allowed: {url}")

    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    data = response.json()

    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON dict, got {type(data).__name__}")

    return data
