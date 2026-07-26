import os
from urllib.parse import urlparse
from typing import Any

import requests


def divide(a: float, b: float) -> float:
    """Divide a by b.
    
    Raises:
        ValueError: If b is zero.
    """
    if b == 0:
        raise ValueError("division by zero")
    return a / b


def is_safe_url(url: str) -> bool:
    """Check if a URL is safe to fetch from (allowlist validation).
    
    Allowed hosts: api.example.com
    Must use http or https scheme.
    Blocks localhost and loopback addresses.
    """
    allowed_hosts = {"api.example.com"}
    
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
    
    # Block localhost/loopback
    if hostname in ("localhost", "127.0.0.1", "0.0.0.0"):
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
        ValueError: If URL is not allowed.
        requests.exceptions.RequestException: On network/HTTP errors.
    """
    if not is_safe_url(url):
        raise ValueError(f"URL not allowed: {url}")
    
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    data = response.json()
    
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON dict, got {type(data).__name__}")
    
    return data
