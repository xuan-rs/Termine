from colorama import (Style, init)
from typing import Literal
from wcwidth import wcwidth
import re
import shutil
import sys
import time
import threading


class Colors:
    init(autoreset=True)
    RED = "\033[31m"
    CYAN = "\033[36m"

    BOLD = Style.BRIGHT

    CYAN_BRIGHT = "\033[96m"

    RESET = "\033[0m"


_console_lock = threading.RLock()
_active_bar: "ProgressBar | None" = None


def _write_log(line: str) -> None:
    with _console_lock:
        bar = _active_bar
        if bar is not None and bar.enabled and bar._last_lines:
            if bar._last_lines > 1:
                sys.stdout.write(f"\033[{bar._last_lines - 1}A")
            sys.stdout.write("\r")
            for i in range(bar._last_lines):
                sys.stdout.write("\033[K")
                if i < bar._last_lines - 1:
                    sys.stdout.write("\n")
            if bar._last_lines > 1:
                sys.stdout.write(f"\033[{bar._last_lines - 1}A")
            sys.stdout.write("\r")
            bar._last_lines = 0
        sys.stdout.write(line + "\n")
        if bar is not None and bar.enabled:
            bar._render_locked()
        sys.stdout.flush()


def faild(content: str) -> None:
    """print Faild content"""
    _write_log(f"[{Colors.RED}{Colors.BOLD}Faild{Colors.RESET}] {content}")

def usage(content: str) -> None:
    """print Usage content"""
    _write_log(f"[{Colors.CYAN_BRIGHT}{Colors.BOLD}Usage{Colors.RESET}] {content}")

def info(content: str) -> None:
    _write_log(f"[{Colors.CYAN_BRIGHT}{Colors.BOLD}Info{Colors.RESET}] {content}")

def please(content: str) -> None:
    _write_log(f"[{Colors.CYAN_BRIGHT}{Colors.BOLD}Please{Colors.RESET}] {content}")

def gradient(text: str, start_rgb: tuple = (0, 240, 240), end_rgb: tuple = (180, 0, 255)) -> str|None:
    """Prints text with an RGB gradient color effect in the terminal."""
    if not text:
        return None

    r1, g1, b1 = start_rgb
    r2, g2, b2 = end_rgb
    length = len(text)

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


def _fmt_size(n: float) -> str:
    n = float(n)
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{int(n)}B" if unit == "B" else f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}PB"

def _fmt_time(sec: float) -> str:
    sec = int(sec)
    if sec < 60:
        return f"{sec}s"
    if sec < 3600:
        return f"{sec // 60}m{sec % 60:02d}s"
    return f"{sec // 3600}h{(sec % 3600) // 60:02d}m"


class ProgressBar:
    def __init__(
        self,
        total: int,
        width: int = 30,
        prefix: str = "",
        unit: Literal["bytes", "files"] = "bytes",
        enabled: bool = True,
    ):
        self.total = max(1, int(total))
        self.width = width
        self.prefix = prefix
        self.unit = unit
        self.enabled = enabled and sys.stdout.isatty()
        self._done = 0
        self._start = time.time()
        self._last_render = 0.0
        self._closed = False
        self._last_lines = 0
        

        global _active_bar
        if self.enabled:
            with _console_lock:
                _active_bar = self
                self._render_locked()
                sys.stdout.flush()

    def update(self, n: int = 1) -> None:
        with _console_lock:
            self._done = min(self._done + n, self.total)
        self._render_throttled()

    def set(self, n: int) -> None:
        with _console_lock:
            self._done = min(int(n), self.total)
        self._render_throttled()

    def close(self) -> None:
        global _active_bar
        if self._closed:
            return
        self._closed = True
        with _console_lock:
            if self.enabled:
                self._done = self.total
                self._render_locked()
                sys.stdout.write("\n")
                sys.stdout.flush()
            if _active_bar is self:
                _active_bar = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def _render_throttled(self) -> None:
        if not self.enabled:
            return
        now = time.time()
        if now - self._last_render < 0.05 and self._done < self.total:
            return
        self._last_render = now
        with _console_lock:
            self._render_locked()
            sys.stdout.flush()

    def _render_locked(self) -> None:
        total = self.total
        done = self._done
        ratio = done / total if total else 0.0
        filled = int(self.width * ratio)
        bar = "█" * filled + "░" * (self.width - filled)
        pct = ratio * 100.0
        elapsed = max(time.time() - self._start, 1e-9)
        speed = done / elapsed

        if self.unit == "files":
            amount = f"{done}/{total}"
            rate = f"{speed:.1f}f/s"
        else:
            amount = f"{_fmt_size(done)}/{_fmt_size(total)}"
            rate = f"{_fmt_size(speed)}/s"

        eta = ""
        if 0 < done < total and speed > 0:
            eta = f" ETA {_fmt_time((total - done) / speed)}"

        bar_line = f"[{bar}] {pct:5.1f}% {amount} {rate}{eta}"

        lines = []
        if self.prefix:
            lines.append(f"↓ {self.prefix}")
        lines.append(bar_line)

        out = ""
        if self._last_lines:
            if self._last_lines > 1:
                out += f"\033[{self._last_lines - 1}A"
            out += "\r"
            for i in range(self._last_lines):
                out += "\033[K"
                if i < self._last_lines - 1:
                    out += "\n"
            if self._last_lines > 1:
                out += f"\033[{self._last_lines - 1}A"
            out += "\r"

        out += "\n".join(lines)
        self._last_lines = len(lines)
        sys.stdout.write(out)


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
            "lt": "├", "rt": "┤", "tt": "┬", "bt": "┴", "cross": "┼"
        },
        "vh_hl": {
            "tl": "┎", "tr": "┒", "bl": "┖", "br": "┚",
            "h": "─", "v": "┃",
            "lt": "┣", "rt": "┫", "tt": "┳", "bt": "┻", "cross": "╂"
        },
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
        "─": 12, "━": 12, "═": 12,
        "│": 3,  "┃": 3,  "║": 3,
        "┼": 15, "╋": 15, "╬": 15,
        "├": 11, "┣": 11, "╠": 11,
        "┤": 7,  "┫": 7,  "╣": 7,
        "┬": 14, "┳": 14, "╦": 14,
        "┴": 13, "┻": 13, "╩": 13,
        "╭": 6,  "┌": 6,  "┏": 6,  "╔": 6,
        "╮": 10, "┐": 10, "┓": 10, "╗": 10,
        "╰": 9,  "└": 9,  "┗": 9,  "╚": 9,
        "╯": 5,  "┘": 5,  "┛": 5,  "╝": 5,
    }

    _CHAR_TO_MASK = {
        "│": 3, "─": 12, "┼": 15,
        "├": 11, "┤": 7, "┬": 14, "┴": 13,
        "┌": 6, "╭": 6, "┐": 10, "╮": 10,
        "└": 9, "╰": 9, "┘": 5, "╯": 5,

        "┃": 19, "━": 28, "╋": 31,
        "┣": 27, "┫": 23, "┳": 30, "┻": 29,
        "┏": 22, "┓": 26, "┗": 25, "┛": 21,

        "║": 3, "═": 12, "╬": 15,
        "╠": 11, "╣": 7, "╦": 14, "╩": 13,
        "╔": 6, "╗": 10, "╚": 9, "╝": 5,

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
             start_x: int = 0,
             start_y: int = 0,
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
        old_mask = self._CHAR_TO_MASK.get(old_char, 0)

        if old_mask > 0 and new_mask > 0:
            merged_mask = old_mask | new_mask
            self.content[y][x] = self._MASK_TO_CHAR.get(merged_mask, "┼")
        elif old_mask == 0:
            self.content[y][x] = self._MASK_TO_CHAR.get(new_mask, " ")

    def draw_line(self, x1: int, y1: int, x2: int, y2: int, is_heavy: bool = False) -> None:
        """Draw a line with auto-merge and true heavy mask support."""
        if y1 == y2:
            for x in range(min(x1, x2), max(x1, x2) + 1):
                if x == min(x1, x2): mask = 8
                elif x == max(x1, x2): mask = 4
                else: mask = 12

                if is_heavy: mask |= 16
                self._merge_mask(x, y1, mask)

        elif x1 == x2:
            for y in range(min(y1, y2), max(y1, y2) + 1):
                if y == min(y1, y2): mask = 2
                elif y == max(y1, y2): mask = 1
                else: mask = 3

                if is_heavy: mask |= 16
                self._merge_mask(x1, y, mask)

    def render(self) -> str:
        self._check()
        return "\n".join(["".join(row) for row in self.content])
