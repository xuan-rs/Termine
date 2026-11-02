import json
import os
import json_repair

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

def repair_json_file(path: str) -> None:
    with open(path, 'r', encoding='utf-8') as f:
        raw = f.read()

    fixed = json_repair.repair_json(raw, return_objects=False)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(fixed)
    os.replace(path, path)
