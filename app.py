API_KEY = "sk-live-secret-key-12345"  # security: hardcoded secret

def divide(a, b):
    return a / b  # peer: no zero check

def fetch(url):
    import requests
    return requests.get(url).json()  # security: SSRF risk
