from network import network
from TermineTui import terminetui
from minecraft import version_install
import mojangApi

def module_versions(args: list[str]) -> None:
    """Retrieve the list of downloadable versions"""
    if not args:
        terminetui.usage("termine -iv <Version_Name>")
        return

    versions = mojangApi.versions()
    if not versions:
        terminetui.faild("Check if the network is connected")
        return

    terminetui.info("Looking for version...")
    version_found: bool = False
    version_dict: dict[str,str] = {}

    for i in versions["versions"]:
        if i["id"] == args[0]:
            terminetui.info("Version found")
            version_found = True
            version_dict.update(i)
            break

    if not version_found:
        terminetui.faild("Version not found")
        return

    version_install.install(version_dict)
