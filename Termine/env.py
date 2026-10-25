import sys
import os


class TermineInfo:
    version: str = "0.1.0"

class SysInfo:
    system: str = sys.platform

class PathInfo:
    # minecraft: str = os.path.join(
    #     os.path.expanduser("~"),
    #     ".minecraft"
    # ) if SysInfo.system == "linux" else os.path.join(
    #     os.getenv("APPDATA"), # type: ignore
    #     ".minecraft"
    # )
    minecraft: str = "/home/xuan-rs/codes/Termine/.minecraft" # debug
    # minecraft: str = os.path.join(os.environ['USERPROFILE'], 'Desktop') # debug
