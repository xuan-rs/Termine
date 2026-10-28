from typing import Literal
from core import config_manager
from TermineTui import terminetui

def module(args) -> None:
    if not args: # termine -c
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

    if type == "mcdir":
        config_manager.Config().minecraft_dir(args[0])
    elif type == "javapath":
        config_manager.Config().java_path(args[0])
