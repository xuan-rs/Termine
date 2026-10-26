from concurrent.futures import ThreadPoolExecutor
from curl_cffi import requests
import urllib.request

def download_file(url: str, save_file: str) -> None:
    urllib.request.urlretrieve(url, save_file)

def json_fetch(url: str) -> dict:
    response = requests.get(url, impersonate="chrome101")
    return response.json()

def download_file_multi(url, path, threads=8, chunk_size=256*1024):
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Encoding": "identity",
    }

    r = requests.get(url, headers={**headers, "Range": "bytes=0-0"},
                     stream=True, allow_redirects=True)
    total = None
    supports_range = False
    if r.status_code == 206:
        cr = r.headers.get("Content-Range", "")
        if "/" in cr:
            total = int(cr.split("/")[-1])
            supports_range = total > 0
    r.close()

    if not supports_range or total is None:
        r = requests.get(url, headers=headers, stream=True, allow_redirects=True)
        try:
            with open(path, "wb") as f:
                for c in r.iter_content(chunk_size):
                    f.write(c)
        finally:
            r.close()
        return path

    threads = max(1, min(threads, total))
    bs = total // threads
    blocks = [(i * bs, total - 1 if i == threads - 1 else (i + 1) * bs - 1)
              for i in range(threads)]

    with open(path, "wb") as f:
        f.truncate(total)

    def _work(start, end):
        h = {**headers, "Range": f"bytes={start}-{end}"}
        r = requests.get(url, headers=h, stream=True, allow_redirects=True)
        try:
            with open(path, "r+b") as f:
                f.seek(start)
                for c in r.iter_content(chunk_size):
                    if c:
                        f.write(c)
        finally:
            r.close()

    with ThreadPoolExecutor(max_workers=threads) as ex:
        for fu in [ex.submit(_work, s, e) for s, e in blocks]:
            fu.result()

    return path