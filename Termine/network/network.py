from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import local
from curl_cffi import requests
from TermineTui import terminetui
import urllib.request
import os


_tls = local()


def _session() -> requests.Session:
    if not hasattr(_tls, "s"):
        _tls.s = requests.Session(impersonate="chrome101")
    return _tls.s


def touch(path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, "w").close()

def download_file(url: str, save_path: str) -> None:
    touch(save_path)
    urllib.request.urlretrieve(url, save_path)


def json_fetch(url: str) -> dict:
    response = requests.get(url, impersonate="chrome101")
    return response.json()


def download_file_multi(url: str, path: str, threads: int = 8, chunk_size: int = 256 * 1024) -> str:
    headers = {"Accept-Encoding": "identity"}

    r = requests.get(url, headers={**headers, "Range": "bytes=0-0"},
                     impersonate="chrome101", stream=True, allow_redirects=True)
    total, supports_range = None, False
    if r.status_code == 206:
        cr = r.headers.get("Content-Range", "")
        if "/" in cr:
            total = int(cr.split("/")[-1])
            supports_range = total > 0
    r.close()

    if not supports_range or total is None or total < 1 * 1024 * 1024 or threads <= 1:
        r = requests.get(url, headers=headers, impersonate="chrome101",
                         stream=True, allow_redirects=True)
        try:
            with open(path, "wb") as f:
                for c in r.iter_content(chunk_size):
                    if c:
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

    def _work(start: int, end: int):
        h = {**headers, "Range": f"bytes={start}-{end}"}
        r = requests.get(url, headers=h, impersonate="chrome101",
                         stream=True, allow_redirects=True)
        try:
            with open(path, "r+b") as f:
                f.seek(start)
                for c in r.iter_content(chunk_size):
                    if c:
                        f.write(c)
        finally:
            r.close()

    try:
        with ThreadPoolExecutor(max_workers=threads) as ex:
            for fu in [ex.submit(_work, s, e) for s, e in blocks]:
                fu.result()
    except Exception:
        os.remove(path)
        raise

    return path


def _download_one(url: str, save_file: str, retries: int = 2, show_info: str|None = None) -> str:
    os.makedirs(os.path.dirname(save_file) or ".", exist_ok=True)
    if os.path.exists(save_file) and os.path.getsize(save_file) > 0:
        return save_file

    if show_info:
        terminetui.info(f"{show_info}{url.rsplit("/", 1)[-1]}")

    last_err = None
    for _ in range(retries + 1):
        try:
            r = _session().get(url, timeout=30)
            if r.status_code != 200:
                raise RuntimeError(f"HTTP {r.status_code}: {url}")
            tmp = save_file + ".part"
            with open(tmp, "wb") as f:
                f.write(r.content)
            os.replace(tmp, save_file)
            return save_file
        except Exception as e:
            last_err = e
    raise last_err # type: ignore


def download_files_batch(tasks: list[tuple[str, str]], workers: int = 32, show_info: str|None = None) -> list[tuple[str, Exception]]:
    failures: list[tuple[str, Exception]] = []
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(_download_one, u, p, show_info=show_info): (u, p) for u, p in tasks}
        for fu in as_completed(futures):
            u, p = futures[fu]
            try:
                fu.result()
            except Exception as e:
                failures.append((u, e))
    return failures
