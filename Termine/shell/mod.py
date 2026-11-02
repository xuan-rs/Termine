from TermineTui import terminetui
from TermineTui.terminetui import Colors
from core.minecraft.module import module as mod

def module(args: list[str]) -> None:
    # print(args)
    if not args or args[0] not in ["install", "uninstall", "list", "search"]:
        terminetui.usage(f"termine -m <{Colors.RED}{Colors.BOLD}install|uninstall|list|search{Colors.RESET}>")
        return

    mcmod = mod.Modules()

    if args[0] == "install":
        args = args[1:]
        if not args:
            terminetui.usage(f"termine -m install <{Colors.RED}{Colors.BOLD}mod_name{Colors.RESET}> <{Colors.RED}{Colors.BOLD}version{Colors.RESET}>")
            return
        mcmod.install(args[0])
    elif args[0] == "uninstall":
        args = args[1:]
        if not args:
            terminetui.usage(f"termine -m uninstall <{Colors.RED}{Colors.BOLD}mod_name{Colors.RESET}> <{Colors.RED}{Colors.BOLD}version{Colors.RESET}>")
            return
        mcmod.uninstall(args[0], args[1])
    elif args[0] == "search":
        args = args[1:]
        if not args:
            terminetui.usage(f"termine -m search <{Colors.RED}{Colors.BOLD}mod_name{Colors.RESET}>")
            return
        mcmod.search(args[0])
    elif args[0] == "list":
        args = args[1:]
        if not args:
            terminetui.usage(f"termine -m list <{Colors.RED}{Colors.BOLD}version{Colors.RESET}>")
            return

    # debug
    # print(args)
