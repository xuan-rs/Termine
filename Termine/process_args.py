from TermineTui import terminetui
from modules import (help, install, version,
    search
)

def process_args(args: list[str]) -> None:
    if not args:
        terminetui.usage("termine -h/--help")
        return
    
    if args[0] in ["-h","--help","help"]:
        help.module()
    elif args[0] in ["-iv","--install-versions","install-version"]:
        install.module_versions(args[1:])
    elif args[0] in ["-v","--version","version"]:
        version.module()
    elif args[0] in ["-s","--search","search"]:
        search.module(args[1:])
    else:
        terminetui.usage("termine -h/--help")
