import sys
import os
# 拿 ~
home = os.path.expanduser("~") 

# 拿 Roaming (只在 Windows 有值)
roaming = os.getenv("APPDATA")


class TermineInfo:
    version: str = "0.1.0"

class SysInfo:
    system: str = sys.platform

class PathInfo:
    minecraft: str = os.path.join(
        os.path.expanduser("~"),
        ".minecraft"
    ) if SysInfo.system == "linux" else os.path.join(
        os.getenv("APPDATA"), # type: ignore
        ".minecraft"
    )
