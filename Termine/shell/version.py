from TermineTui import terminetui
import env

def module() -> None:
    version = env.TermineInfo.version
    print(terminetui.gradient(f"Termine {version}"))
