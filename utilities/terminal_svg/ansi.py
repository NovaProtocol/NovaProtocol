"""ANSI SGR parsing — converts escape-coded text into styled segments.

Supports colors, bold/italic/underline, reset, and a custom delay escape
(``\\x1b[<ms>p``) that pauses the timeline at that point.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

# Base palette
BG = "#0D1117"
FG = "#c8d2dc"
GREEN = "#50c878"
GREEN_DIM = "#3aa75f"
GRAY = "#828c9b"
BLUE = "#6ea0eb"
RED = "#ff5555"
YELLOW = "#e6c85a"
PINK = "#e678be"

FONT = "DejaVu Sans Mono, Menlo, Consolas, monospace"

# Standard ANSI SGR foreground codes -> hex.
ANSI_FG = {
    "30": "#000000", "31": RED, "32": "#50c878", "33": YELLOW,
    "34": BLUE, "35": PINK, "36": "#8be9fd", "37": FG,
    "90": GRAY, "91": RED, "92": "#50c878", "93": YELLOW,
    "94": BLUE, "95": PINK, "96": "#8be9fd", "97": "#ffffff",
}

_SGR = re.compile(r"\x1b\[([0-9;]*)m")
_DELAY = re.compile(r"\x1b\[(\d+)p")


@dataclass
class Style:
    fg: str = FG
    bold: bool = False
    italic: bool = False
    underline: bool = False


@dataclass
class Segment:
    text: str
    style: Style
    delay: float = 0.0  # pause (seconds) before this segment's first char


def _apply_code(style: Style, code: str) -> None:
    code = code or "0"
    if code == "0":
        style.fg = FG
        style.bold = False
        style.italic = False
        style.underline = False
    elif code == "1":
        style.bold = True
    elif code == "3":
        style.italic = True
    elif code == "4":
        style.underline = True
    elif code == "39":
        style.fg = FG
    elif code in ANSI_FG:
        style.fg = ANSI_FG[code]


def parse_ansi(text: str, base: Style | None = None) -> list[Segment]:
    """Split ``text`` on SGR escapes and custom delays.

    Returns a list of ``Segment`` objects. Escape codes are stripped from the
    output; each segment's ``delay`` is the accumulated pause before it.
    """
    style = Style() if base is None else Style(**vars(base))
    segments: list[Segment] = []

    tokens = []
    for m in _SGR.finditer(text):
        tokens.append((m.start(), m.end(), "sgr", m.group(1)))
    for m in _DELAY.finditer(text):
        tokens.append((m.start(), m.end(), "delay", m.group(1)))
    tokens.sort(key=lambda t: t[0])

    pos = 0
    delay_acc = 0.0
    for start, end, kind, val in tokens:
        if start > pos:
            segments.append(Segment(text[pos:start], Style(**vars(style)), delay_acc))
            delay_acc = 0.0
        if kind == "sgr":
            for c in ([x for x in val.split(";") if x] or ["0"]):
                _apply_code(style, c)
        else:
            delay_acc += int(val) / 1000.0
        pos = end

    if pos < len(text):
        segments.append(Segment(text[pos:], Style(**vars(style)), delay_acc))
    return segments if segments else [Segment("", Style(**vars(style)), delay_acc)]
