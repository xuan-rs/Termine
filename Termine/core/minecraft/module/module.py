from TermineTui import terminetui
from network import network

class Modules:
    def __init__(self) -> None:
        self.mod_name: str

    def install(self, mod_name: str) -> None:
        self.mod_name = mod_name

    def uninstall(self, mod_name: str, version: str) -> None:
        self.mod_name = mod_name

    def search(self, mod_name: str) -> None:
        self.mod_name = mod_name

        url: str = f'https://api.modrinth.com/v2/search?query={mod_name}&facets=[["project_type:mod"]]'
        json: dict = network.json_fetch(url)

        # debug
        # print(json)

        count: int = json["limit"] # 搜索到的mods数量
        mods: list[dict] = json["hits"] # 搜索到的mods列表

        terminetui.info(f"Search Results: ({count})")
        for mod, num in zip(mods, range(1, count + 1)):
            print()
            terminetui.info(f"Result {num}")
            terminetui.info(f"Title: {mod['title']}")
            terminetui.info(f"Categories:")
            for category in mod["categories"]:
                print(f"  - {category}")
            terminetui.info(f"Versions: {mod['versions'][0]}~{mod['versions'][-1]}")

    # def install(self,
    #     categories: Literal["fabric"],
    #     # api: Literal["modrinth", "curseforge"],
    #     mod_name: str,
    # ) -> None:
    #     self.mod_name = mod_name
    #     # self.api = api

    #     if categories == "fabric":
    #         self._fabric()
