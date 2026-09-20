"""Minimal FIGlet renderer for the bundled ANSI Shadow font.

The badge art is generated from a real FIGlet font file (`apps/fonts/ansi_shadow.flf`)
rather than a hand-copied block of characters, so the output matches the widely
used ANSI Shadow font exactly and a new name needs no hand-drawing.

Only the subset of the FIGlet format this font uses is implemented: a `flf2a`
header, optional comment lines, then one fixed-height glyph per character
starting at ASCII 32, each terminated by the endmark from the header.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

_FONT_PATH = Path(__file__).parent / "fonts" / "ansi_shadow.flf"


@lru_cache(maxsize=1)
def _load_font() -> tuple[int, str, dict[str, list[str]]]:
    """Parse the bundled font into (height, endmark, {char: rows})."""
    raw = _FONT_PATH.read_text(encoding="utf-8").split("\n")
    header = raw[0].split()

    signature = header[0]
    if not signature.startswith("flf2a"):
        raise ValueError(f"not a FIGlet font: {signature!r}")

    hardblank = signature[len("flf2a")]
    height = int(header[1])
    # header[5] is the number of comment lines to skip after the header.
    comment_lines = int(header[5]) if len(header) > 5 else 0

    body = raw[1 + comment_lines:]
    # Find the endmark: the last character on the first glyph row.
    endmark = body[0].rstrip("\r")[-1]

    glyphs: dict[str, list[str]] = {}
    pos = 0
    code = 32
    while pos + height <= len(body):
        rows = []
        complete = True
        for i in range(height):
            line = body[pos + i].rstrip("\r")
            if not line:
                complete = False
                break
            rows.append(line)
        if not complete:
            break
        pos += height

        # Strip the endmark run from the final row, then the endmark from each.
        cleaned = []
        for i, line in enumerate(rows):
            if i == height - 1:
                line = line.rstrip(endmark)
            cleaned.append(line.replace(endmark, "").replace(hardblank, " "))
        glyphs[chr(code)] = cleaned
        code += 1

    return height, endmark, glyphs


def render(text: str) -> list[str]:
    """Render `text` as a list of lines in the ANSI Shadow font.

    Unknown characters fall back to a blank cell so a name never raises.
    """
    height, _endmark, glyphs = _load_font()
    blank = [" " * 6] * height
    rows = [""] * height
    for char in text:
        cell = glyphs.get(char, blank)
        for i in range(height):
            rows[i] += cell[i]
    # The font right-pads every glyph, so trim the trailing run.
    return [row.rstrip() for row in rows]
