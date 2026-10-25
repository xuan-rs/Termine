from TermineTui import terminetui
import mojangApi

# Make sure to import colors
RED = terminetui.Colors.RED
BOLD = terminetui.Colors.BOLD
RESET = terminetui.Colors.RESET

def module(args: list[str]) -> None:
    if not args or not args[0].strip():
        terminetui.usage("termine -s <Version_Name>")
        return

    keyword = args[0].strip().lower()
    versions = mojangApi.versions()
    if not versions:
        terminetui.faild("Check if the network is connected")
        return

    versions = versions["versions"]
    filtered_versions = [v for v in versions if keyword in v["id"].lower()]

    if not filtered_versions:
        terminetui.faild(f"No versions found matching '{args[0]}'.")
        return

    max_size = max(len(v["id"]) for v in filtered_versions)

    screen = terminetui.Render(width=max_size + 29, height=len(filtered_versions) + 2)
    screen.quad("rounded")
    screen.draw_line(max_size+3, 0, max_size+3, len(filtered_versions)+1)
    screen.draw_line(max_size+15, 0, max_size+15, len(filtered_versions)+1)
    
    for y_idx, version_dict in enumerate(filtered_versions, start=1):
        v_id = version_dict["id"]
        
        # 1. Find the keyword position in the version id
        # Use .lower() to find correctly, but extract from original v_id
        idx = v_id.lower().find(keyword)
        
        if idx != -1:
            # 2. Split into three parts
            part1 = v_id[:idx]
            part2 = v_id[idx:idx+len(keyword)]
            part3 = v_id[idx+len(keyword):]
            # 3. Reconstruct with color codes
            colored_id = f"{part1}{RED}{BOLD}{part2}{RESET}{part3}"
        else:
            colored_id = v_id
        # 4. Render the highlighted string
        screen.text(
            content=colored_id,
            start_x=2,
            start_y=y_idx
        )
        screen.text(
            content=version_dict["type"],
            start_x=max_size+5,
            start_y=y_idx,
            width=10,
            height=1
        )
        screen.text(
            content=version_dict["releaseTime"],
            start_x=max_size+17,
            start_y=y_idx,
            width=10,
            height=1
        )

    print(screen.render())
    return
