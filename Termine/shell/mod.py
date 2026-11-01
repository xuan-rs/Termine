from TermineTui import terminetui
from core.minecraft.module import module as mod

def module(args: list[str]) -> None:
    # print(args)
    if not args or args[0] not in ["install", "uninstall", "list", "search"]:
        terminetui.usage("termine -m <install|uninstall|list|search>")
        return

    mcmod = mod.Modules()

    if args[0] == "install":
        args = args[1:]
        if not args:
            terminetui.usage("termine -m install <mod_name>")
            return
        mcmod.install(args[0])
    elif args[0] == "uninstall":
        args = args[1:]
        if not args:
            terminetui.usage("termine -m uninstall <mod_name> <version>")
            return
        mcmod.uninstall(args[0], args[1])
    elif args[0] == "search":
        args = args[1:]
        if not args:
            terminetui.usage("termine -m search <mod_name>")
            return
        mcmod.search(args[0])
    elif args[0] == "list":
        args = args[1:]
        if not args:
            terminetui.usage("termine -m list <version>")
            return

    # debug
    # print(args)
