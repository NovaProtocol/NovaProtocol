"""Renderer — emits the SVG from a timeline.

Two animation modes:

- **begin-based** (``loop=False``): ``begin="<t>s" dur="0.01s" fill="freeze"``.
  Most reliably supported in browsers, but plays once.
- **keyTimes loop** (``loop=True``): all animations share one master duration
  with ``repeatCount="indefinite"`` so the whole sequence loops in sync.

Scroll model (matches a real console):
- ``max_line`` rows visible in a clipped viewport.
- Every row shifts up by ``LINE_H`` at each overflow row's begin time.
"""

from __future__ import annotations

import svgwrite
from svgwrite import animate

from utilities.terminal_svg.ansi import BG, FONT, Style
from utilities.terminal_svg.timeline import Row, Timeline

# Layout constants
PAD_X = 26
BODY_TOP = 60
FONT_SIZE = 14
LINE_H = 20
CHAR_W = 8.4


def _char_style(style: Style) -> dict:
    return {
        "fill": style.fg,
        "font_weight": "bold" if style.bold else "normal",
        "font_style": "italic" if style.italic else "normal",
        "text_decoration": "underline" if style.underline else "none",
    }


def _flash(el, appear_t: float):
    """Make the element visible at appear_t (opacity 0 -> 1), held forever."""
    el.add(animate.Animate(
        attributeName="opacity",
        values="0;1",
        begin=f"{appear_t:.3f}s",
        dur="0.01s",
        fill="freeze",
    ))


def _y_chain(el, init_y: float, scroll_times: list[float]):
    """Chain per-line y jumps: at each scroll event, shift up by LINE_H."""
    y = init_y
    for st in scroll_times:
        prev = y
        y -= LINE_H
        el.add(animate.Animate(
            attributeName="y",
            values=f"{prev:.1f};{y:.1f}",
            begin=f"{st:.3f}s",
            dur="0.01s",
            fill="freeze",
        ))


def _loop_animate(el, attr: str, appear_t: float, total: float, values=("0", "1")):
    """KeyTimes animate: instant jump at appear_t, loops with the master dur."""
    k = appear_t / total if total > 0 else 0.0
    k = max(0.0, min(1.0, k))
    el.add(animate.Animate(
        attributeName=attr,
        values=";".join(values),
        keyTimes=f"0;{k:.5f};{k:.5f};1",
        dur=f"{total:.3f}s",
        begin="0s",
        repeatCount="indefinite",
    ))


def _loop_y_chain(el, init_y: float, scroll_times: list[float], total: float):
    """KeyTimes y-chain: hold, jump LINE_H at each scroll event, loops."""
    y_ms: list[tuple[float, float]] = [(0.0, init_y)]
    y = init_y
    for st in scroll_times:
        y_ms.append((st - 0.001, y))
        y -= LINE_H
        y_ms.append((st, y))
    y_ms.append((total, y))

    kt = [max(0.0, min(1.0, t / total)) for t, _ in y_ms]
    # enforce non-decreasing keyTimes
    for i in range(1, len(kt)):
        if kt[i] < kt[i - 1]:
            kt[i] = kt[i - 1]
    vals = [f"{y:.1f}" for _, y in y_ms]
    el.add(animate.Animate(
        attributeName="y",
        values=";".join(vals),
        keyTimes=";".join(f"{k:.5f}" for k in kt),
        dur=f"{total:.3f}s",
        begin="0s",
        repeatCount="indefinite",
    ))


def render_svg(
    timeline: Timeline,
    max_line: int,
    width: int,
    loop: bool = False,
) -> str:
    rows: list[Row] = timeline.rows
    R = len(rows)
    total = timeline.total

    content_h = max_line * LINE_H
    height = BODY_TOP + content_h + 6

    dwg = svgwrite.Drawing(viewBox=f"0 0 {width} {height}")

    # Chrome
    dwg.add(dwg.rect(insert=(0, 0), size=(width, height), fill=BG))
    dwg.add(dwg.rect(insert=(6, 6), size=(width - 12, height - 12),
                      fill="#0b0f14", stroke="#30353e", stroke_width=1, rx=4))
    dwg.add(dwg.rect(insert=(6, 6), size=(width - 12, 26), fill="#161b22", rx=4))
    title = dwg.text("nova@ProjectNova: ~ \u2014 bash",
                     insert=(PAD_X, 24), font_family=FONT, font_size=12, fill="#828c9b")
    title["xml:space"] = "preserve"
    dwg.add(title)

    # Viewport clip: exactly max_line rows
    clip = dwg.clipPath(id="term_viewport")
    clip.add(dwg.rect(insert=(6, BODY_TOP - FONT_SIZE),
                       size=(width - 12, content_h)))
    dwg.add(clip)
    viewport = dwg.g(clip_path="url(#term_viewport)")

    content = dwg.g()

    # Overflow rows (beyond max_line) trigger the per-line scroll shifts.
    scroll_times = [row.begin for row in rows[max_line:]]

    for i, row in enumerate(rows):
        init_y = BODY_TOP + i * LINE_H
        is_command = row.kind == "command"

        te = dwg.text("", insert=(PAD_X, init_y),
                      font_family=FONT, font_size=FONT_SIZE)
        te["xml:space"] = "preserve"  # keep column-aligned spaces

        if is_command:
            for ch in row.chars:
                span = dwg.tspan(ch.text, **_char_style(ch.style), opacity="0")
                if loop:
                    _loop_animate(span, "opacity", ch.begin, total)
                else:
                    _flash(span, ch.begin)
                te.add(span)
        else:
            # Output: split into same-style segments so multi-color lines work.
            segments: list[tuple[str, Style]] = []
            for ch in row.chars:
                if segments and segments[-1][1] == ch.style:
                    segments[-1] = (segments[-1][0] + ch.text, ch.style)
                else:
                    segments.append((ch.text, ch.style))
            if not segments:
                segments = [("", Style())]
            for seg_text, seg_style in segments:
                span = dwg.tspan(seg_text, **_char_style(seg_style), opacity="0")
                if loop:
                    _loop_animate(span, "opacity", row.begin, total)
                else:
                    _flash(span, row.begin)
                te.add(span)

        # Every row shifts up LINE_H at each overflow event (uniform shift).
        if scroll_times:
            if loop:
                _loop_y_chain(te, init_y, scroll_times, total)
            else:
                _y_chain(te, init_y, scroll_times)

        content.add(te)

    viewport.add(content)
    dwg.add(viewport)

    return dwg.tostring()
