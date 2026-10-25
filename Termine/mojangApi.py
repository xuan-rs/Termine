from network import network

def versions() -> dict:
    """Retrieve the list of downloadable versions"""
    url = "https://piston-meta.mojang.com/mc/game/version_manifest.json"
    network.jsonUrl_fetch(url)
    return network.jsonUrl_fetch(url)
