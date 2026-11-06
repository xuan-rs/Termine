import json
import os
import json_repair
import shutil
import subprocess
import re

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

def java_major(version_str: str) -> str:
    parts = version_str.split(".")
    if parts[0] == "1" and len(parts) > 1:
        return parts[1]
    return parts[0]

def java_version(java_path: str|None) -> dict[str,str]:
    """get java version and path"""
    try:
        if not java_path:
            java = "java"
        else:
            java = java_path

        result = subprocess.run(
            [java, '-version'],
            capture_output=True,
            text=True,
            check=False
        )
        output = result.stderr.strip()
        
        version_match = re.search(r'version "([^"]+)"', output)
        if not version_match:
            version_match = re.search(r'version (\S+)', output)
        
        version_str = version_match.group(1) if version_match else None
        
        java_path = None
        for line in output.splitlines():
            if ' version ' in line or 'Runtime Environment' in line:
                continue
            if java in line.lower():
                pass
            
        java_path = shutil.which('java')
        
        return {
            'version': java_major(str(version_str)),
            'path': str(java_path),
        }
    except FileNotFoundError:
        return {}
