from pathlib import Path
import os
import subprocess

import env
from TermineTui import terminetui
from .. import toolkit

def game(path: str) -> None:
    version_dir = Path(path).expanduser().resolve()
    version_name = version_dir.name
    version_info = toolkit.read_json(str(version_dir / f"{version_name}.json"))
    minecraft_dir = Path(env.PathInfo.minecraft_dir)

    libraries_dir = minecraft_dir / "libraries"
    libraries = sorted(
        str(library)
        for library in libraries_dir.rglob("*.jar")
        if "-natives-" not in library.name
    )
    client_jar = version_dir / f"{version_name}.jar"
    classpath = os.pathsep.join([*libraries, str(client_jar)])

    start_command: list[str] = [
        env.PathInfo.java_path,
        "-Xmx4G",
        f"-Djava.library.path={version_dir / 'natives'}",
        "-cp",
        classpath,
        version_info["mainClass"],
        "--username",
        "Steve",
        "--version",
        version_name,
        "--gameDir",
        str(minecraft_dir),
        "--assetsDir",
        str(minecraft_dir / "assets"),
        "--assetIndex",
        version_info["assetIndex"]["id"],
        "--uuid",
        "00000000000000000000000000000000",
        "--accessToken",
        "0",
        "--userType",
        "legacy",
        "--versionType",
        "release",
    ]

    terminetui.info(f"Starting Minecraft {version_name}...")
    subprocess.run(start_command, check=True)
