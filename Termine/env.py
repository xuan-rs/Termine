from core import config_manager
from dataclasses import dataclass
import sys
import os

APPDATA: str = os.getenv("APPDATA") # type: ignore
EXPANDUSER: str = os.path.expanduser("~")

def _minecraftpath() -> str:
    return config_manager.Config().minecraft_dir(None) # type: ignore

def _configpath() -> str:
    return os.path.join(
        EXPANDUSER,
        ".config", "termine"
    ) if SysInfo.system == "linux" else os.path.join(
        APPDATA, # type: ignore
        "termine"
    )


class TermineInfo:
    version: str = "0.0.5"

class SysInfo:
    system: str = sys.platform

@dataclass
class PathInfo:
    config_path: str = _configpath()
    minecraft_dir: str = _minecraftpath()
