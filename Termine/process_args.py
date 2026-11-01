from TermineTui import terminetui
import shell


_COMMAND_MAP = [
    (shell.install,                         ("-iv", "--install-versions", "install-version")),
    (shell.search,                          ("-s",  "--search",           "search")),
    (shell.config,                          ("-c",  "--config",           "config")),
    (shell.game,                            ("-g",  "--game",             "game")),
    (shell.mod,                             ("-m",  "--mod",              "mod")),
    (lambda _: shell.help(),                ("-h",  "--help",             "help")),
    (lambda _: shell.version(),             ("-v",  "--version",          "version")),
    (lambda args: shell.config(args, True), ("-c!", "--config!",          "config!")),
]


def process_args(args: list[str]) -> None:
    if len(args) == 0:
        shell.default()
        return

    main_cmd = args[0]

    for command, flags in _COMMAND_MAP:
        if main_cmd in flags:
            command(args)
            return

    terminetui.usage("termine -h/--help/help")
