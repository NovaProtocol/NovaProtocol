# Rendering (`utilities/terminal_svg/render.py`)

Turns a `Timeline` into an SVG string — the final output served as `image/svg+xml` with SMIL `<animate>` tags.

## Layout Constants

```python
PAD_X = 26
BODY_TOP = 60
FONT_SIZE = 14
LINE_H = 20
CHAR_W = 8.4  # not used for layout (monospace is implicit), kept for reference
```

- `BODY_TOP` is the title bar height — content starts at that `y`.
- `LINE_H` is the scroll stride — each overflow row shifts every row up by exactly this many pixels.
- `width` defaults to `880` (`TerminalSVG.width`); `height = BODY_TOP + max_line*LINE_H + 6`.
- `PAD_X` is the left inset of every `tspan` row.

## `render_svg(timeline, max_line, width, loop=False) -> str`

### Signature

```python
def render_svg(
    timeline: Timeline,
    max_line: int,
    width: int,
    loop: bool = False,
) -> str:
```

- `timeline.rows` — ordered rows from `build_timeline()`, each with `chars: list[Char]` and `begin`.
- `max_line` — visible viewport rows; beyond that, scrolling kicks in.
- `width` — SVG `viewBox` width.
- `loop` — if `True`, use `keyTimes`/`repeatCount="indefinite"` master-duration loops; if `False`, use `begin="…s" dur="0.01s" fill="freeze"` one-shot. Badge renderers use `loop=False` (plays once — most reliable).

Returns `dwg.tostring()` — an `<?xml …><svg …>` string ready to serve.

### Modes

| `loop` | Per-char visibility | Per-row scroll | Total duration |
|--------|---------------------|----------------|----------------|
| `False` (default) | `opacity 0→1 begin="…s" dur="0.01s" fill="freeze"` | `y` chain of `begin="…s"` jumps | `timeline.total` — not embedded, just the last `begin`’s freeze |
| `True` | `keyTimes` `0;k;k;1` loop over `total` | `keyTimes` `y` chain over `total` | `total` embedded as `dur="…s"` with `repeatCount="indefinite"` |

Badge modules (`name_svg`, `console_svg`, `skills_svg`) keep `loop=False` — the GitHub profile image renders once; a looping badge would flicker on every camo reload. The `__main__.py` demo may toggle `loop=True` for a self-replaying preview.

### Chrome

```python
dwg.add(dwg.rect(insert=(0, 0), size=(width, height), fill=BG))  # #0D1117 outer
dwg.add(
    dwg.rect(
        insert=(6, 6),
        size=(width - 12, height - 12),
        fill="#0b0f14",
        stroke="#30353e",
        stroke_width=1,
        rx=4,
    )
)  # inner
dwg.add(dwg.rect(insert=(6, 6), size=(width - 12, 26), fill="#161b22", rx=4))  # title bar
title = dwg.text(
    "nova@ProjectNova: ~ — bash", insert=(PAD_X, 24), font_family=FONT, font_size=12, fill="#828c9b"
)
```

Colors mirror VS Code / GitHub Dark. The inner fill `#0b0f14` is slightly darker than `BG` so the rounded border reads. The title is static — not animated.

### Viewport Clip

```python
clip = dwg.clipPath(id="term_viewport")
clip.add(
    dwg.rect(insert=(6, BODY_TOP - FONT_SIZE), size=(width - 12, content_h))
)  # content_h = max_line * LINE_H
dwg.add(clip)
viewport = dwg.g(clip_path="url(#term_viewport)")
```

Exactly `max_line` rows visible; anything above/below is clipped. No scrollbar — content scrolls via `y` shifts.

### Per-Row Groups

For each `Row i`:

- `init_y = BODY_TOP + i * LINE_H`.
- A `<text x=PAD_X y=init_y font-family=FONT font-size=14 xml:space="preserve">` group — `preserve` keeps column-aligned spaces (important for `df -h`, `ss -tlnp` tables).
- Inside:

  - If `kind == "command"`: one `<tspan>` per `Char` (per-character typing).
  - If `kind == "output"`: coalesce consecutive `Char`s with the same `Style` into one `<tspan>` (keeps multi-color lines like `ERROR` red + path gray in a single `tspan` per segment, opacity-animated as a unit at `row.begin`).

  Each `<tspan>` starts `opacity="0"` and gets one `<animate>`:

  - Non-loop: `_flash(span, begin)` → `opacity 0;1 begin="…s" dur="0.01s" fill="freeze"`.
  - Loop: `_loop_animate(span, "opacity", begin, total)` → `keyTimes`-based loop.

- Then chaining for scroll:

  ```python
  scroll_times = [row.begin for row in rows[max_line:]]
  ```

  At each `st`, every earlier row's `y` animates `prev;prev-LINE_H` with `begin="st s"`. Overflow rows themselves also shift — they start below the viewport and scroll up into view at their `begin`.

  - Non-loop: `_y_chain(text_el, init_y, scroll_times)`.
  - Loop: `_loop_y_chain(text_el, init_y, scroll_times, total)` — `keyTimes` loop with holds and `LINE_H` jumps.

## Flash Helper

```python
def _flash(el, appear_t: float):
    el.add(
        animate.Animate(
            attributeName="opacity",
            values="0;1",
            begin=f"{appear_t:.3f}s",
            dur="0.01s",
            fill="freeze",
        )
    )
```

`dur="0.01s"` is the smallest perceptible — effectively "instant at `appear_t`". `freeze` holds the final value forever (no loop).

## Loop Helpers

```python
def _loop_animate(el, attr: str, appear_t: float, total: float, values=("0", "1")):
    k = appear_t / total
    el.add(
        animate.Animate(
            attributeName=attr,
            values=";".join(values),
            keyTimes=f"0;{k:.5f};{k:.5f};1",
            dur=f"{total:.3f}s",
            begin="0s",
            repeatCount="indefinite",
        )
    )
```

`keyTimes` holds at `"0"` until `k`, jumps to `"1"` at that instant, holds to `1`. Clamped to `[0,1]`.

## Scroll Geometry Example

`max_line=8`, 12 rows total → `scroll_times = rows[8].begin, rows[9].begin, rows[10].begin, rows[11].begin` — 4 jumps.

- Row 0: `init_y = 60` → at `rows[8].begin` → `40` → at `rows[9].begin` → `20` → `0` → `-20` (clipped).
- Row 8 (first overflow): `init_y = 220` → before its `begin` it is below the clip (`content_h = 160` → viewport `y` range ~`46–206`), at its `begin` it stays at `220` but its `opacity` fades in and immediately all rows shift — so it slides into the last visible slot.

## Font & Sizing

- `FONT = "DejaVu Sans Mono, Menlo, Consolas, monospace"` — same family as the GH profile's rendered canvas; metrics assume monospace.
- `CHAR_W` is not used for layout — `svgwrite` + `text`/`tspan` with `xml:space="preserve"` relies on the viewer's monospace advance, not manual `x` stepping.
- Badge NOVA art (46 chars per line) was tuned for `880` width — `46 * 8.4 ≈ 386` + chrome, well inside 880.

## Sys Dependencies

- `svgwrite>=1.4,<2` (runtime dep in `requirements.txt`).
- `fonts-dejavu-core` installed in the `Dockerfile` via `apt-get` — ensures `DejaVu Sans Mono` metrics are stable in the slim image (GitHub camo and local browsers may use any fallback monospace if the font is missing, but the image's `python3 -m compileall` check would still pass).

## Testing

`tests/test_terminal_svg.py`:

```python
def test_terminal_svg_renders_last_max_lines():
    v = TerminalSVG(max_line=3)
    for i in range(5):
        v.add_line({"input": f"cmd{i}", "output": [f"out{i}"]})
    svg = v.render()
    assert svg.startswith("<svg")
    assert 'attributeName="opacity"' in svg


def test_terminal_svg_height_scales():
    v = TerminalSVG(max_line=20)
    v.add_line({"input": "x", "output": []})
    assert "466" in svg  # BODY_TOP(60)+20*20+6
```

Set `loop=True` in a test and assert `repeatCount="indefinite"` appears.

## Gotchas

- `width` is caller-controlled — `TerminalSVG(width=880)` is the default, but `/name.svg` may render wider if NOVA art exceeds 880; the viewBox is `0 0 {width} {height}`, so the image scales to the `<img>` element’s width.
- `scroll_times` is recomputed from `rows[max_line:]` inside `render_svg`, not passed — so even if `build_timeline` grouped entries differently, scrolling still triggers exactly when the `max_line+1`th row appears.
- `height` ignores loop geometry — same formula for both modes; the keyTimes `y` chain includes the final `total` as a keyTime but the clip height is fixed.
