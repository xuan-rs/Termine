from TermineTui import terminetui
from TermineTui.terminetui import Colors
from pathlib import Path
from core.minecraft import version_game
import os

def _complete_path(path: str) -> str:
    path = path.replace("\\", "/")
    return str(Path(path).expanduser().resolve())

def module(args: list[str]) -> None:
    if not args:
        terminetui.usage(f"termine game <{Colors.RED}{Colors.BOLD}Version Folder Path{Colors.RESET}>")
        return

    if not os.path.exists(_complete_path(args[0])):
        terminetui.faild("Path not exists.")
        return

    version_game.game(args[0])
