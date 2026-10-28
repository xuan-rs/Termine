from TermineTui import terminetui
from network import network
from .. import toolkit
from os.path import join as pathjoin
import env
import os
import time
import zipfile
import platform

mcdir: str = env.PathInfo.minecraft_dir


def _rule_matches(rule: dict, system: str) -> bool:
    os_rule = rule.get("os")
    if os_rule:
        name = os_rule.get("name")
        if name and name != system:
            return False
        arch = os_rule.get("arch")
        if arch:
            machine = platform.machine().lower()
            if machine in ("amd64", "x64"):
                machine = "x86_64"
            elif machine in ("i386", "i686"):
                machine = "x86"
            elif machine in ("aarch64", "arm64"):
                machine = "arm64"
            if arch == "aarch_64":
                arch = "arm64"
            if machine != arch:
                return False
    features = rule.get("features")
    if features and any(features.values()):
        return False
    return True

# def _library_allowed(lib: dict, system: str) -> bool:
#     rules = lib.get("rules")
#     if not rules:
#         return True
#     allowed = False
#     for rule in rules:
#         if _rule_matches(rule, system):
#             allowed = rule.get("action") == "allow"
#     return allowed


def _index_jsonfile(version_name: str, version_info: dict) -> str:
    """download the index Json file"""
    assets_index_path = pathjoin(mcdir,
        "assets",
        "indexes",
        f"{version_name}.json"
    )

    os.makedirs(os.path.dirname(assets_index_path), exist_ok=True)

    terminetui.info(f"Download {version_info["assetIndex"]["sha1"]}...")
    network.download_file(
        version_info["assetIndex"]["url"],
        assets_index_path,
        True
    )
    return assets_index_path

def _resource_files(assets_index_path: str) -> None:
    """download resource files"""
    terminetui.info("Downloading resource files...")
    time.sleep(0.5)

    objects: dict = toolkit.read_json(assets_index_path)["objects"]

    small_tasks = []
    large_tasks = []
    seen = set()

    for obj in objects.values():
        h = obj["hash"]
        if h in seen:
            continue
        seen.add(h)

        url = f"https://resources.download.minecraft.net/{h[:2]}/{h}"
        save_path = pathjoin(mcdir, "assets", "objects", h[:2], h)
        if obj["size"] > 4 * 1024 * 1024:
            large_tasks.append((url, save_path))
        else:
            small_tasks.append((url, save_path))

    failures = network.download_files_batch(small_tasks, workers=32, show_info="Downloading ")
    for url, save_path in large_tasks:
        try:
            network.download_file_multi(url, save_path, threads=4)
        except Exception as e:
            failures.append((url, e))

    if failures:
        for url, exc in failures:
            print(url, exc)

def _libraries(libraries: list, version_name: str) -> None:
    ...
    tasks = []
    natives_jars = []
    for lib in libraries:
        artifact = lib.get("downloads", {}).get("artifact")
        if not artifact or "url" not in artifact:
            continue
        path = pathjoin(mcdir, "libraries", artifact["path"])
        tasks.append((artifact["url"], path))
        if ":natives-" in lib.get("name", "") or "-natives-" in artifact["path"]:
            natives_jars.append(path)

    failures = network.download_files_batch(tasks, workers=32, show_info="Downloading ")
    ...

    natives_dir = pathjoin(mcdir, "versions", version_name, "natives")
    os.makedirs(natives_dir, exist_ok=True)
    for jar in natives_jars:
        with zipfile.ZipFile(jar) as zf:
            for name in zf.namelist():
                if name.startswith("META-INF/") or name.endswith("/"):
                    continue
                zf.extract(name, natives_dir)

def _client_jar(version_name: str, version_info: dict) -> str:
    client = version_info["downloads"]["client"]
    save_path = pathjoin(mcdir, "versions", version_name, f"{version_name}.jar")
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    if os.path.exists(save_path) and os.path.getsize(save_path) == client["size"]:
        return save_path

    terminetui.info(f"Downloading client {version_name}.jar")
    if client["size"] > 4 * 1024 * 1024:
        network.download_file_multi(client["url"], save_path, threads=8)
    else:
        network.download_file(client["url"], save_path)
    return save_path


def install(version: dict[str, str]) -> None:
    terminetui.info("Parse version...")

    # {
    #     'id': '1.20.1',
    #     'type': 'release',
    #     'url': 'https://piston-meta.mojang.com/v1/packages/38d412af3b247e485c7f7e50ac25febc4e79ab1d/1.20.1.json',
    #     'time': '2026-10-20T06:48:44+00:00', 'releaseTime': '2023-06-12T13:25:51+00:00'
    # }

    version_name = version["id"]
    version_url = version["url"]

    version_info = network.json_fetch(version_url)


    assets_index_path = _index_jsonfile(version_name, version_info)
    _resource_files(assets_index_path)
    _libraries(version_info["libraries"], version_name)
    _client_jar(version_name, version_info)

    toolkit.write_json(pathjoin(mcdir,"versions",version_name,f"{version_name}.json"),version_info)

    terminetui.info("Ok.")
