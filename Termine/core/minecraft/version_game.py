from pathlib import Path
from TermineTui import terminetui
from .. import toolkit
from string import Template
import subprocess
import os
import env
import json

def parse_arguments_legacy(arguments: dict) -> list[str]:
    Template(s).substitute(auth_player_name="Steve", auth_session="abc123")

d = {"b": "hello", "a": "${b}"}
d["a"] = Template(d["a"]).substitute(d)
print(d)   # {'b': 'hello', 'a': 'hello'}

def parse_arguments_modern(arguments: dict) -> tuple[list[str], list[str]]:
    pass

def game(path: str) -> None:
    """start the game with the specified version"""
    terminetui.info(f"Parse version...")

    version_dir = Path(path).expanduser().resolve()
    version_name = version_dir.name
    version_info = toolkit.read_json(str(version_dir / f"{version_name}.json"))
    minecraft_dir = Path(os.path.dirname(path))

    # minecraft_dir = Path(env.PathInfo.minecraft_dir)

    client_jar = version_dir / f"{version_name}.jar"

    start_command: list[str] = []

    mainClass = version_info["mainClass"]
    need_javaVersion = str(version_info["javaVersion"]["majorVersion"])

    java_path = env.PathInfo.java_path
    java_version = toolkit.java_version(java_path)["version"].split(".")[0]

    try:
        if java_version != need_javaVersion or toolkit.java_version(java_path)["version"] == {}:
            terminetui.faild(f"Please use Java {need_javaVersion}")
            return
    except PermissionError:
        terminetui.faild(f"Permission denied to access Java at {java_version}. Please check your permissions.")
        return
    except OSError:
        terminetui.faild(f"The Java version cannot be executed. Please verify if the version is available and executable.")
        return

    if need_javaVersion != java_version: # java version detection
        terminetui.faild(f"Please use Java {need_javaVersion} for gaming.")
        return

    if "arguments" in version_info:
        jvm_args: list[str]
        game_args: list[str]
        jvm_args, game_args = parse_arguments_modern(version_info["arguments"])
    else:
        args = parse_arguments_legacy(version_info["minecraftArguments"])

    terminetui.info(f"Starting Minecraft {version_name}...")

    # subprocess.run(start_command, check=True)
