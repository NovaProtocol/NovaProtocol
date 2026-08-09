from __future__ import annotations

import svgwrite
from svgwrite import animate

FONT = "DejaVu Sans Mono, Menlo, Consolas, monospace"
BG = "#0D1117"
GREEN = "#50c878"
GREEN_DIM = "#3aa75f"
FG = "#c8d2dc"
GRAY = "#828c9b"
BLUE = "#6ea0eb"
PINK = "#e678be"
YELLOW = "#e6c85a"
RED = "#ff5555"
CYAN = "#79c0ff"


class TypeWriter:
    """Reveals text left-to-right on the timeline via a clip-path width animation."""

    def __init__(self, dwg: svgwrite.Drawing) -> None:
        self.dwg = dwg
        self._seq = 0

    def typed(self, group, text, x, baseline, size, color, begin, dur, max_w=1000):
        seq = self._seq
        self._seq += 1
        cid = f"tp{seq}"
        clip = self.dwg.clipPath(id=cid)
        rect = self.dwg.rect(insert=(x, baseline - size), size=(0, size * 1.6))
        rect.add(
            animate.Animate(
                attributeName="width",
                values=["0", str(max_w)],
                begin=f"{begin:.3f}s",
                dur=f"{dur:.3f}s",
                fill="freeze",
            )
        )
        clip.add(rect)
        group.add(clip)
        el = self.dwg.text(
            text,
            insert=(x, baseline),
            font_family=FONT,
            font_size=size,
            fill=color,
            clip_path=f"url(#{cid})",
        )
        group.add(el)
        return el

    def plain(self, group, text, x, baseline, size, color):
        return group.add(
            self.dwg.text(
                text,
                insert=(x, baseline),
                font_family=FONT,
                font_size=size,
                fill=color,
            )
        )
