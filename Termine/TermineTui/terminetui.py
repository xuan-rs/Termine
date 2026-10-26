from colorama import (Style, init)
from typing import Literal
from wcwidth import wcwidth
import re
import shutil


class Colors:
    init(autoreset=True)
    RED = "\033[31m"
    CYAN = "\033[36m"

    BOLD = Style.BRIGHT

    CYAN_BRIGHT = "\033[96m"

    RESET = "\033[0m"


def faild(content: str) -> None:
    """print Faild content"""
    print(f"[{Colors.RED}{Colors.BOLD}Faild{Colors.RESET}] {content}")

def usage(content: str) -> None:
    """print Usage content"""
    print(f"[{Colors.CYAN_BRIGHT}{Colors.BOLD}Usage{Colors.RESET}] {content}")

def info(content: str) -> None:
    print(f"[{Colors.CYAN_BRIGHT}{Colors.BOLD}Info{Colors.RESET}] {content}")

def gradient(text: str, start_rgb: tuple = (0, 240, 240), end_rgb: tuple = (180, 0, 255)) -> str|None:
    """Prints text with an RGB gradient color effect in the terminal."""
    if not text:
        return None

    r1, g1, b1 = start_rgb
    r2, g2, b2 = end_rgb
    length = len(text)
    
    # Reset color state first to prevent terminal pollution
    result = "\033[0m" 
    
    for i, char in enumerate(text):
        if char.isspace():
            result += char
            continue
            
        ratio = i / max(1, length - 1)
        r = int(r1 + (r2 - r1) * ratio)
        g = int(g1 + (g2 - g1) * ratio)
        b = int(b1 + (b2 - b1) * ratio)
        result += f"\033[38;2;{r};{g};{b}m{char}"
        
    return result + "\033[0m"


class Render:
    _STYLES = {
        "light": {
            "tl": "┌", "tr": "┐", "bl": "└", "br": "┘", 
            "h": "─", "v": "│",
            "lt": "├", "rt": "┤", "tt": "┬", "bt": "┴", "cross": "┼"
        },
        "heavy": {
            "tl": "┏", "tr": "┓", "bl": "┗", "br": "┛", 
            "h": "━", "v": "┃",
            "lt": "┣", "rt": "┫", "tt": "┳", "bt": "┻", "cross": "╋"
        },
        "double": {
            "tl": "╔", "tr": "╗", "bl": "╚", "br": "╝", 
            "h": "═", "v": "║",
            "lt": "╠", "rt": "╣", "tt": "╦", "bt": "╩", "cross": "╬"
        },
        "rounded": {
            "tl": "╭", "tr": "╮", "bl": "╰", "br": "╯", 
            "h": "─", "v": "│",
            # Rounded corners don't have dedicated tees, fallback to light style
            "lt": "├", "rt": "┤", "tt": "┬", "bt": "┴", "cross": "┼"
        },
        # Mix & Match styles
        # Vertical Heavy, Horizontal Light
        # Common use: Thick outer borders, thin inner dividers
        "vh_hl": {
            "tl": "┎", "tr": "┒", "bl": "┖", "br": "┚", 
            "h": "─", "v": "┃",
            "lt": "┣", "rt": "┫", "tt": "┳", "bt": "┻", "cross": "╂"
        },
        # Vertical Light, Horizontal Heavy
        # Common use: Thin outer borders, thick inner dividers
        "vl_hh": {
            "tl": "┍", "tr": "┑", "bl": "┕", "br": "┙", 
            "h": "━", "v": "│",
            "lt": "┝", "rt": "┥", "tt": "┯", "bt": "┷", "cross": "┿"
        }
    }

        # Bitmask: N=1, S=2, W=4, E=8
    
    _MASK_TO_CHAR = {
        3: "│", 12: "─", 15: "┼", 11: "├", 7: "┤", 14: "┬", 13: "┴", 
        6: "┌", 10: "┐", 9: "└", 5: "┘", 1: "╵", 2: "╷", 4: "╴", 8: "╶",
        
        19: "┃", 28: "━", 31: "╋", 27: "┣", 23: "┫", 30: "┳", 29: "┻",
        22: "┏", 26: "┓", 25: "┗", 21: "┛",
    
        17: "╻", 18: "╹", 20: "╸", 24: "╺"
    }

    _LINE_MASKS = {
        " ": 0,
        "─": 12, "━": 12, "═": 12, # Horizontal
        "│": 3,  "┃": 3,  "║": 3,  # Vertical
        "┼": 15, "╋": 15, "╬": 15, # Cross
        "├": 11, "┣": 11, "╠": 11, # Left Tee (N,S,E)
        "┤": 7,  "┫": 7,  "╣": 7,  # Right Tee (N,S,W)
        "┬": 14, "┳": 14, "╦": 14, # Top Tee (S,W,E)
        "┴": 13, "┻": 13, "╩": 13, # Bottom Tee (N,W,E)
        "╭": 6,  "┌": 6,  "┏": 6,  "╔": 6,  # Top Left (S,E)
        "╮": 10, "┐": 10, "┓": 10, "╗": 10, # Top Right (S,W)
        "╰": 9,  "└": 9,  "┗": 9,  "╚": 9,  # Bottom Left (N,E)
        "╯": 5,  "┘": 5,  "┛": 5,  "╝": 5,  # Bottom Right (N,W)
    }

    _CHAR_TO_MASK = {
        # --- Light ---
        "│": 3, "─": 12, "┼": 15,
        "├": 11, "┤": 7, "┬": 14, "┴": 13,
        "┌": 6, "╭": 6, "┐": 10, "╮": 10, 
        "└": 9, "╰": 9, "┘": 5, "╯": 5,
        
        # --- Heavy ---
        "┃": 19, "━": 28, "╋": 31,
        "┣": 27, "┫": 23, "┳": 30, "┻": 29,
        "┏": 22, "┓": 26, "┗": 25, "┛": 21,

        # --- Double ---
        "║": 3, "═": 12, "╬": 15,
        "╠": 11, "╣": 7, "╦": 14, "╩": 13,
        "╔": 6, "╗": 10, "╚": 9, "╝": 5,

        # --- Dead ends ---
        "╵": 1, "╷": 2, "╴": 4, "╶": 8,
    }

    def __init__(self, width: int = 60, height: int = 5):
        self.width = width
        self.height = height
        self.content: list[list[str]] = [[" " for _ in range(width)] for _ in range(height)]

        self.tm_width = shutil.get_terminal_size().columns
        self.tm_height = shutil.get_terminal_size().lines

    def _check(self) -> None:
        if self.width > self.tm_width:
            for y in range(self.height):
                self.content[y] = self.content[y][:self.tm_width]
            self.width = self.tm_width

    def quad(self, 
             line: Literal["light", "heavy", "double", "rounded"], 
             start_x: int = 0,  # <--- 起始列
             start_y: int = 0,  # <--- 起始行
             width: int|None = None, 
             height: int|None = None
             ) -> None:
        """render quadrilateral\n
        : line   - [light   ┌─┐]\n
        :        - [heavy   ┗━┛]\n
        :        - [double  ╔═╗]\n
        :        - [rounded ╰─╯]\n
        : width  - The width of a quadrilateral\n
        : height - The height of a quad"""
        
        if width is None: width = self.width
        if height is None: height = self.height
        
        string = self._STYLES[line]
        
        for h in range(height):
            for w in range(width):
                target_y = start_y + h
                target_x = start_x + w
                
                if target_y >= self.height or target_x >= self.width:
                    continue
                
                if h == 0: 
                    if w == 0: self.content[target_y][target_x] = string["tl"]
                    elif w == width - 1: self.content[target_y][target_x] = string["tr"]
                    else: self.content[target_y][target_x] = string["h"]
                elif h == height - 1: 
                    if w == 0: self.content[target_y][target_x] = string["bl"]
                    elif w == width - 1: self.content[target_y][target_x] = string["br"]
                    else: self.content[target_y][target_x] = string["h"]
                else: 
                    if w == 0 or w == width - 1: 
                        self.content[target_y][target_x] = string["v"]
                    else: 
                        self.content[target_y][target_x] = " " 

    def text(self,
            content: str,
            start_x: int = 0,
            start_y: int = 0,
            width: int = 0,
            height: int = 0,
        ) -> None:
        """write content in tui"""
        if width <= 0:
            width = self.width - start_x
        if height <= 0:
            height = self.height - start_y

        cursor_x = start_x
        cursor_y = start_y
        row_offset = 0
        last_pos = None
        pending_ansi = ""
        ANSI_ESCAPE = re.compile(r'(\033\[[0-9;]*m)')

        tokens = ANSI_ESCAPE.split(content)

        for token in tokens:
            if not token:
                continue

            if ANSI_ESCAPE.match(token):
                pending_ansi += token
                continue

            for c in token:
                w = wcwidth(c)
                if w < 0:
                    continue

                if w == 0:
                    if last_pos is not None:
                        ly, lx = last_pos
                        self.content[ly][lx] += pending_ansi + c
                        pending_ansi = ""
                    continue

                if row_offset + w > width:
                    cursor_x = start_x
                    cursor_y += 1
                    row_offset = 0
                    pending_ansi = ""

                if cursor_y - start_y >= height:
                    return

                if not (0 <= cursor_y < self.height and 0 <= cursor_x < self.width):
                    cursor_x += w
                    row_offset += w
                    pending_ansi = ""
                    continue

                self.content[cursor_y][cursor_x] = pending_ansi + c
                pending_ansi = ""
                last_pos = (cursor_y, cursor_x)

                if w == 2:
                    if cursor_x + 1 < self.width:
                        self.content[cursor_y][cursor_x + 1] = ""
                    else:
                        self.content[cursor_y][cursor_x] = pending_ansi + " "
                        last_pos = None
                        cursor_x += 1
                        row_offset += 1
                        continue

                cursor_x += w
                row_offset += w
        if pending_ansi and last_pos is not None:
            ly, lx = last_pos
            self.content[ly][lx] += pending_ansi

    def _merge_mask(self, x: int, y: int, new_mask: int) -> None:
        """Merge bitmask at (x, y) and auto-resolve the character."""
        if not (0 <= x < self.width and 0 <= y < self.height):
            return
            
        old_char = self.content[y][x]
        # Get current mask from old character
        old_mask = self._CHAR_TO_MASK.get(old_char, 0)
        
        # If both are lines, OR them together
        if old_mask > 0 and new_mask > 0:
            merged_mask = old_mask | new_mask
            # Lookup the best matching character
            # If not found, fallback to standard cross or space
            self.content[y][x] = self._MASK_TO_CHAR.get(merged_mask, "┼")
        elif old_mask == 0:
            # If it's just a space, place the new line character directly
            self.content[y][x] = self._MASK_TO_CHAR.get(new_mask, " ")

    def draw_line(self, x1: int, y1: int, x2: int, y2: int, is_heavy: bool = False) -> None:
        """Draw a line with auto-merge and true heavy mask support."""
        if y1 == y2:  # Horizontal
            for x in range(min(x1, x2), max(x1, x2) + 1):
                if x == min(x1, x2): mask = 8   # Right only
                elif x == max(x1, x2): mask = 4 # Left only
                else: mask = 12                 # Left + Right
                
                if is_heavy: mask |= 16         # Add heavy flag
                self._merge_mask(x, y1, mask)
                
        elif x1 == x2:  # Vertical
            for y in range(min(y1, y2), max(y1, y2) + 1):
                if y == min(y1, y2): mask = 2   # Down only
                elif y == max(y1, y2): mask = 1 # Up only
                else: mask = 3                  # Up + Down
                
                if is_heavy: mask |= 16         # Add heavy flag
                self._merge_mask(x1, y, mask)

    def render(self) -> str:
        self._check()
        return "\n".join(["".join(row) for row in self.content])

# if __name__ == "__main__": # debug
#     screen = Render()
#     screen.quad(line="rounded")
#     screen.quad(line="heavy",start_x=2, start_y=1, width=5, height=3)
#     screen.text("浇洒嗲世界大都市建设宽带端口速度较快的就是看得见啊是肯德基阿谁看到asd阿谁",
#         start_x=8,
#         start_y=1,
#         width=30,
#         height=3
#     )

#     print(screen.render())
