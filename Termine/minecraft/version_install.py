from TermineTui import terminetui
from network import network
import env
import os
import json
import zipfile

def install(version_dict: dict[str, str]) -> None:
    terminetui.info("Resolving version...")

    # 1. Fetch version manifest (the main version JSON)
    version_data = network.jsonUrl_fetch(version_dict["url"])
    if not version_data:
        terminetui.faild("Check if the network is connected")
        return

    # 2. Fetch asset index JSON
    terminetui.info("Fetching asset index...")
    asset_index_data = network.jsonUrl_fetch(version_data["assetIndex"]["url"])
    if not asset_index_data:
        terminetui.faild("Failed to fetch asset index")
        return

    # 3. Save the asset index to .minecraft/assets/indexes/<version_id>.json
    minecraft_path: str = env.PathInfo.minecraft
    filepath: str = os.path.join(
        minecraft_path,
        "assets", "indexes",
        f"{version_dict['id']}.json"  # Use single quotes inside f-string for compatibility
    )
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(asset_index_data, f, ensure_ascii=False, indent=4)

    # 4. Download all assets (objects)
    terminetui.info("Downloading assets...")
    objects = asset_index_data.get("objects", {})
    
    # objects is a dictionary: { "logical/path": {"hash": "xxx", "size": 123} }
    for logical_path, file_info in objects.items():
        file_hash = file_info["hash"]
        prefix = file_hash[:2]  # First 2 chars of hash
        url = f"https://resources.download.minecraft.net/{prefix}/{file_hash}"
        save_path = os.path.join(
            minecraft_path, "assets", "objects",
            prefix, file_hash
        )
        # Check if file already exists to save bandwidth
        if not os.path.exists(save_path):
            network.download_file(url, save_path)

    # 5. Download <Version>.jar
    terminetui.info("Downloading '.jar'...")

    version_dirpath: str = os.path.join(minecraft_path, "versions", version_dict["id"])
    os.makedirs(version_dirpath, exist_ok=True) # Added exist_ok=True to prevent crash
    
    # Fixed the quote nesting syntax error here
    jar_filename = f"{version_dict['id']}.jar" 
    network.download_file(
        version_data["downloads"]["client"]["url"],
        os.path.join(version_dirpath, jar_filename)
    )

    # 6. Download libraries
    terminetui.info("Downloading libraries...")

    # Normalize architecture (e.g., AMD64 -> x86_64, aarch64 -> arm64)
    current_arch = getattr(env.SysInfo, 'arch', 'x86_64').lower()
    if current_arch in ["amd64", "x64"]:
        current_arch = "x86_64"
    elif current_arch in ["aarch64", "armv8"]:
        current_arch = "arm64"

    def is_library_allowed(lib: dict, current_os: str, current_arch: str) -> bool:
        """Check if the library is applicable for the current OS and CPU architecture based on the 'rules' array."""
        if "rules" not in lib:
            return True

        allowed = False
        for rule in lib["rules"]:
            action = rule.get("action")
            os_info = rule.get("os", {})
            os_name = os_info.get("name")
            os_arch = os_info.get("arch")

            # Skip if the rule specifies a different OS or architecture
            if (os_name and os_name != current_os) or (os_arch and os_arch != current_arch):
                continue

            if action == "allow":
                allowed = True
            elif action == "disallow":
                allowed = False
        return allowed

    def extract_natives(jar_path: str, dest_dir: str) -> None:
        """
        Extract native binaries (.dll, .so, .dylib) from a JAR file.\n
        Files are flattened to the root of dest_dir to ensure JVM -Djava.library.path can find them.
        """
        with zipfile.ZipFile(jar_path, 'r') as z:
            for file in z.namelist():
                if file.endswith(('.dll', '.so', '.dylib')) and 'META-INF' not in file:
                    filename = os.path.basename(file)
                    target_path = os.path.join(dest_dir, filename)
                    
                    # Prevent overwriting to avoid conflicts in legacy modded environments
                    if not os.path.exists(target_path):
                        with z.open(file) as source, open(target_path, "wb") as target:
                            target.write(source.read())

    natives_dir = os.path.join(minecraft_path, "versions", version_dict["id"], "natives")
    os.makedirs(natives_dir, exist_ok=True)
    
    classpath_entries: list[str] = []

    for lib in version_data["libraries"]:
        if not is_library_allowed(lib, env.SysInfo.system, current_arch):
            continue

        downloads = lib.get("downloads", {})
        artifact = downloads.get("artifact")

        # Handle both standard libraries and modern natives (1.19+)
        if artifact:
            artifact_path = os.path.join(minecraft_path, "libraries", artifact["path"])
            os.makedirs(os.path.dirname(artifact_path), exist_ok=True)
            
            if not os.path.exists(artifact_path):
                network.download_file(artifact["url"], artifact_path)

            if "natives" in artifact["path"]:
                extract_natives(artifact_path, natives_dir)
            else:
                classpath_entries.append(artifact_path)

        # Handle legacy natives (1.12 and below)
        natives = lib.get("natives")
        if natives:
            classifier_key = natives.get(env.SysInfo.system)
            if classifier_key:
                arch_suffix = "64" if "64" in current_arch else "32"
                classifier_key = classifier_key.replace("${arch}", arch_suffix)

                native_artifact = downloads.get("classifiers", {}).get(classifier_key)
                if native_artifact:
                    native_path = os.path.join(minecraft_path, "libraries", native_artifact["path"])
                    os.makedirs(os.path.dirname(native_path), exist_ok=True)
                    
                    if not os.path.exists(native_path):
                        network.download_file(native_artifact["url"], native_path)
                    
                    extract_natives(native_path, natives_dir)

    # 7 log_config
    logging_url = version_data["logging"]["client"]["file"]["url"]
    logging_path = os.path.join(
        minecraft_path,
        "assets",
        "log_configs"
    )
    network.download_file(logging_url, logging_path)

    terminetui.info("Asset download complete!")
