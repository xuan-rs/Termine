from TermineTui import terminetui
import env

CYAN = terminetui.Colors.CYAN
RESET = terminetui.Colors.RESET
BOLD = terminetui.Colors.BOLD

version = f"Termine {env.TermineInfo.version}"
version = terminetui.gradient(text=version)

def _get_screen() -> str:
    # 1. Layout Configuration (No more magic numbers!)
    SCREEN_WIDTH = 81
    SCREEN_HEIGHT = 11
    
    # Outer Box Padding
    PADDING_X = 2
    
    # Inner Table Dimensions
    TABLE_START_X = 2
    TABLE_START_Y = 4
    TABLE_WIDTH = 78
    TABLE_HEIGHT = 6
    
    # Column X Coordinates (Start points for text and lines)
    # Calculated based on the inner table start_x
    COL1_TEXT_X = 4
    COL2_LINE_X = 8
    COL2_TEXT_X = 10
    COL3_LINE_X = 29
    COL3_TEXT_X = 31
    COL4_LINE_X = 48
    COL4_TEXT_X = 50
    
    # Table Content Y Start
    ROW_START_Y = 5
    
    # 2. Command Data Structure
    # Format: (Short Flag, Long Flag, Module Name, Description)
    COMMANDS_DATA = [
        ("-h",  "--help",             "help",             "* command list | help"),
        ("-iv", "--install-versions", "install-versions", "* install versions"),
        ("-v",  "--version",          "version",          "* termine version"),
        ("-s",  "--search",           "search",           "* search versions")
    ]

    # 3. Rendering Phase
    screen = terminetui.Render(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
    screen.quad("rounded")

    # Header
    screen.text(version, start_x=PADDING_X, start_y=1) # type: ignore
    screen.text(f"{CYAN}{BOLD}Commands List{RESET}", start_x=PADDING_X, start_y=3)
    screen.draw_line(0, 2, SCREEN_WIDTH - 1, 2)

    # Inner Table Box
    screen.quad(
        line="heavy",
        start_x=TABLE_START_X,
        start_y=TABLE_START_Y,
        width=TABLE_WIDTH,
        height=TABLE_HEIGHT
    )

    # Draw Vertical Dividers
    screen.draw_line(COL2_LINE_X, TABLE_START_Y, COL2_LINE_X, TABLE_START_Y + TABLE_HEIGHT - 1, True)
    screen.draw_line(COL3_LINE_X, TABLE_START_Y, COL3_LINE_X, TABLE_START_Y + TABLE_HEIGHT - 1, True)
    screen.draw_line(COL4_LINE_X, TABLE_START_Y, COL4_LINE_X, TABLE_START_Y + TABLE_HEIGHT - 1, True)

    # Render Rows (Automatically loops through data)
    for i, (short_flag, long_flag, module_name, desc) in enumerate(COMMANDS_DATA):
        current_y = ROW_START_Y + i
        screen.text(short_flag,  start_x=COL1_TEXT_X, start_y=current_y)
        screen.text(long_flag,   start_x=COL2_TEXT_X, start_y=current_y)
        screen.text(module_name, start_x=COL3_TEXT_X, start_y=current_y)
        screen.text(desc,        start_x=COL4_TEXT_X, start_y=current_y)

    return screen.render()

help: str = _get_screen()

def module() -> None:
    print(help)
    return