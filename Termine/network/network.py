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

import requests
import os
from pathlib import Path

def download_file(url: str, save_path: str) -> bool:
    """
    Download a file from a given URL to a specific local path.
    Supports streaming to handle large files efficiently.
    
    :param url: The URL to download from.
    :param save_path: The local path to save the file (including filename).
    :return: True if successful, False otherwise.
    """
    try:
        # 1. Ensure the parent directory exists
        path = Path(save_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # 2. Start the download stream
        # stream=True prevents loading the whole file into memory
        with requests.get(url, stream=True, timeout=15) as response:
            response.raise_for_status() # Raise an exception for bad status codes (404, 500, etc.)
            
            # 3. Write chunks to disk
            with open(path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        
        return True
        
    except requests.exceptions.RequestException as e:
        # Handle network errors
        print(f"Network error during download: {e}")
        return False
    except OSError as e:
        # Handle file system errors (e.g., permission denied, disk full)
        print(f"File system error: {e}")
        return False
