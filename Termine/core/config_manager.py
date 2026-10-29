from . import toolkit
from TermineTui import terminetui
from pathlib import Path
import sys
import os

def _config_path() -> str:
    """Resolve Termine's config directory.\n
    (moved here from env.py so config_manager no longer depends on env)
    """
    if sys.platform.startswith("linux"):
        return os.path.join(os.path.expanduser("~"), ".config", "termine")
    return os.path.join(os.getenv("APPDATA"), "termine")  # type: ignore[arg-type]

PATH: str = _config_path()

class Config:
    def __init__(self) -> None:
        self.config_file = os.path.join(PATH, "config.json")

        # os.makedirs(PATH, exist_ok=True)

    # def language(self, lang: Literal["en_US"])

    # def _fix_config_file(self) -> None

    def _read_config(self) -> dict:
        """Read Termine's configuration file"""
        return toolkit.read_json(self.config_file)

    def _complete_path(self, path: str) -> str:
        path = path.replace("\\", "/")
        return str(Path(path).expanduser().resolve())

    def minecraft_dir(self, path: str|None) -> str|None:
        """set .minecraft path or check\n
        : path - If None, returns the path from config.\n
                If a path is provided, creates the director
        """
        if not path:
            # .get() so a fresh install (empty config) does not raise KeyError
            return self._read_config().get("minecraft_dir")

        path = self._complete_path(path)

        file_content = self._read_config()
        if file_content == {}:
            file_content = {"minecraft_dir": path}
        else:
            file_content["minecraft_dir"] = path

        toolkit.write_json(self.config_file, file_content)

        try:
            os.path.exists(path)
        except PermissionError:
            terminetui.faild("No permission to access")
            terminetui.please("sudo/administrator is required, proceed with caution")

        return

    def java_path(self, path: str|None) -> str|None:
        """set .minecraft path or check\n
        : path - If None, returns the path from config.\n
                If a path is provided, creates the director
        """
        if not path:
            # .get() so a fresh install (empty config) does not raise KeyError
            return self._read_config().get("java_path")

        path = self._complete_path(path)

        file_content = self._read_config()

        if file_content == {}:
            file_content = {"java_path": path}
        else:
            file_content["java_path"] = path

        # NOTE: original code forgot to persist the change; added below
        toolkit.write_json(self.config_file, file_content)
        # os.makedirs(path, exist_ok=True)
        return
