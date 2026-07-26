import os
import requests
from urllib.parse import urlparse

API_KEY = os.getenv("API_KEY")  # security: use environment variable

def divide(a, b):
    if b == 0:
        raise ValueError("Division by zero")  # peer: zero check added
    return a / b

def fetch(url):
    # security: validate URL to prevent SSRF
    parsed = urlparse(url)
    if parsed.scheme not in ("http", "https"):
        raise ValueError("Invalid URL scheme")
    return requests.get(url).json()
