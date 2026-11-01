from typing import Literal
from TermineTui import terminetui
from network import network

class Modules:
    def __init__(self) -> None:
        self.mod_name: str

    def search(self,
        categories: Literal["fabric"],
        mod_name: str,
        version: str
    ) -> None:
        def fabric() -> None:
            url: str = f'https://api.modrinth.com/v2/search?query={mod_name}&facets=[["categories:{categories}"],["versions:{version}"],["project_type:mod"]]'
            json: dict = network.json_fetch(url)

            # debug
            print(json)
        
        self.mod_name = mod_name

        if categories == "fabric":
            fabric()

    # def install(self,
    #     categories: Literal["fabric"],
    #     # api: Literal["modrinth", "curseforge"],
    #     mod_name: str,
    # ) -> None:
    #     self.mod_name = mod_name
    #     # self.api = api

    #     if categories == "fabric":
    #         self._fabric()
