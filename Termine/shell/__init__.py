from importlib import import_module

def help():
    return import_module(".help", __package__).module()

def version():
    return import_module(".version", __package__).module()

def install(args: list[str]):
    return import_module(".install", __package__).module_versions(args)

def search(args: list[str]):
    return import_module(".search", __package__).module(args)

def config(args: list[str], force: bool = False):
    return import_module(".config", __package__).module(args[1:], force)

def game(args: list[str]):
    return import_module(".game", __package__).module(args)

def default() -> None:
    from TermineTui import terminetui
    terminetui.usage("termine -h/--help/help")
