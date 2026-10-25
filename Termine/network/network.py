import socket
import requests

def network_available(host="8.8.8.8", port=53, timeout=2.0) -> bool:
    try:
        socket.create_connection((host, port), timeout=timeout)
        return True
    except OSError:
        return False

def jsonUrl_fetch(url: str) -> dict:
    if not network_available():
        return {}
    data: dict = requests.get(url).json()
    return data
