from typing import Literal
from core import config_manager
from TermineTui import terminetui
from pathlib import Path
import env
import subprocess
import os
import sys
import shutil

def _complete_path(path: str) -> str:
    path = path.replace("\\", "/")
    return str(Path(path).expanduser().resolve())

def _java_test(path: str) -> bool:
    if not path:
        return False
    if os.path.isdir(path):
        path = os.path.join(path, "bin", "java.exe" if env.SysInfo.system == "win32" else "java")
    exe = shutil.which(path)
    if not exe:
        return False
    cmd = ["cmd", "/c", exe] if exe.lower().endswith((".bat", ".cmd")) else [exe]
    try:
        r = subprocess.run(cmd + ["-version"], capture_output=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return False
    out = b"".join(filter(None, (r.stderr, r.stdout)))
    return b'version "' in out

def module(args, mandatory: bool = False) -> None:
    if not args: # termine -c >s<
        terminetui.usage("termine -c mcdir|javapath|-c/--check/check")
        return

    name = args[0] # termine -c >mcdir<
    type: Literal["mcdir", "javapath"]

    if name in ["--mcdir", "mcdir"]: # termine -c mcdir
        type = "mcdir"
    elif name in ["--java-path", "javapath"]: # termine -c javapath
        type = "javapath"
    else: # termine -c ?
        terminetui.usage("termine -c mcdir|javapath|-c/--check/check"); return

    args = args[1:] # termine -c mcdir ><

    if not args:
        if type == "mcdir": # termine -c mcdir
            terminetui.usage("termine -c mcdir <Path>"); return
        elif type == "javapath": # termine -c javapath
            terminetui.usage("termine -c javapath <Path>"); return

    if not os.path.exists(_complete_path(args[0])) and not mandatory:
        terminetui.faild("Path not exists.")
        return

    if type == "mcdir":
        config_manager.Config().minecraft_dir(args[0])
    elif type == "javapath":
        if not _java_test(args[0]) and not mandatory:
            terminetui.faild("Java version not available, '-c!' mandatory configuration")
        config_manager.Config().java_path(args[0])
