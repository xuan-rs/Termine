from TermineTui import terminetui
from network import network
import env
import os
import json

def install(version_dict: dict[str,str]) -> None:
    version = network.jsonUrl_fetch(version_dict["url"])
    terminetui.info("Resolving version...")

    if not version:
        terminetui.faild("Check if the network is connected")

    filepath: str = os.path.join(
        env.PathInfo.minecraft,
        "assets", "indexes",
        f"{version_dict["id"]}.json"
    )
    os.makedirs(os.path.dirname(filepath), exist_ok=True) # /home/user-name/.minecraft/assets/indexes/

    with open(filepath, "w", encoding="utf-8")as f:
        json.dump(version, f, ensure_ascii=False, indent=4)
