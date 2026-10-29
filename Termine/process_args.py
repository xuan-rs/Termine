from TermineTui import terminetui

def process_args(args: list[str]) -> None:
    if not args:
        terminetui.usage("termine -h/--help")
        return
    arg = args[0]
    
    if arg in ["-h","--help","help"]:
        from modules import help
        help.module()
    elif arg in ["-iv","--install-versions","install-version"]:
        from modules import install
        install.module_versions(args[1:])
    # elif arg in ["-im","--install-mod","install-mod"]:
    #     install.module_mod(args[1:])
    elif arg in ["-v","--version","version"]:
        from modules import version
        version.module()
    elif arg in ["-s","--search","search"]:
        from modules import search
        search.module(args[1:])
    elif arg in ["-c","--config","config"]:
        from modules import config
        config.module(args[1:])
    elif arg in ["-c!","--config!","config!"]:
        from modules import config
        config.module(args[1:],True)
    elif arg in ["-g","--game","game"]:
        from modules import game
        game.module(args[1:])
    else:
        terminetui.usage("termine -h/--help")
