import json
import os

def write_json(path:str, content:dict, indent:int = 4) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8")as f:
        json.dump(content, f, indent=indent)
    return

def read_json(path:str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8")as f:
        return json.load(f)
