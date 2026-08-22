# Terminal SVG — Overview

`utilities/terminal_svg` is a **standalone, reusable library** that turns a scripted terminal session into an animated SVG. It has **no dependency on `apps/`** — it is importable on its own, runnable via `__main__.py`, and consumed by the three badge modules (`apps/name_svg.py`, `apps/console_svg.py`, `apps/skills_svg.py`) only through its public API.

## What It Does

- Takes a session described as a list of entries — each entry is a command you typed plus the lines the shell printed back.
- Turns each line into per-character events with absolute `begin` times (seconds into the animation).
- Emits a fixed-size SVG with SMIL `<animate>` tags that type the prompt, type the command, flash each output line, and scroll when `max_line` is exceeded — mimicking a real console window.

```
Entry dicts  →  TerminalSVG  →  build_timeline()  →  render_svg()  →  SVG string
```

No JavaScript, no external assets — everything that animates is an `<animate attributeName="opacity">` or `<animate attributeName="y">` inside a `<tspan>`.

## Layout

```
utilities/terminal_svg/
├── __init__.py    # Public surface — re-exports TerminalSVG, Style, parse_ansi, palette
├── __main__.py    # Demo: build a tiny session, write temp SVG, open in browser
├── ansi.py        # SGR parsing, palette, Style, Segment, parse_ansi()
├── timeline.py    # build_timeline(), Char, Row, Timeline
├── render.py      # render_svg(), layout constants, chrome, clipping
└── core.py        # TerminalSVG class — the facade you actually use
```

- [`ANSI Parsing`](ansi.md) — how `\x1b[32m`, `\x1b[1;4m`, `\x1b[0m`, and the custom `\x1b[<ms>p` pause are split into `Segment`s.
- [`Timeline Engine`](timeline.md) — how entries become `Row`s of `Char`s with `begin` times, respecting per-entry and view-wide delays.
- [`Rendering`](render.md) — how `Timeline` + `max_line` becomes a clipped, scrollable SVG with SMIL.
- [`Core API`](core.md) — the `TerminalSVG` facade — fields, `add_line()`, `clear()`, `render()`.

## Quick Start

```python
from utilities.terminal_svg import TerminalSVG

view = TerminalSVG(max_line=10)
view.command_prefix = "nova@ProjectNova:~$ "
view.delay_per_char_input = 0.08  # typing feel for what you type
view.delay_per_char_output = 0.0  # output appears instantly
view.delay_per_line_input = 1.0  # prompt shows, then a beat before typing
view.delay_per_line_output = 0.05  # pause before each output line

view.add_line({"input": "ls", "output": ["file.txt"]})
view.add_line(
    {
        "input": "cat file.txt",
        "output": ["hello world"],
        "custom_prefix": "root@box:~# ",
        "custom_start_delay": 0.5,
        "custom_end_delay": 0.2,
    }
)

svg = view.render()  # SVG string — write to file or return as Response
svg = view.render(width=900)  # override width if needed
```

Serve it as FastAPI does:

```python
from fastapi.responses import Response


@app.get("/demo.svg")
async def demo():
    return Response(
        content=view.render(),
        media_type="image/svg+xml",
        headers={"Cache-Control": "no-store, max-age=0"},
    )
```

Standalone demo:

```bash
python -m utilities.terminal_svg          # writes /tmp/*.svg and opens it
python -m utilities.terminal_svg --help   # (no args — it runs the embedded demo)
```

## Design Choices

| Choice | Why |
|--------|-----|
| SMIL `<animate>` instead of CSS/JS | Works inside `<img>` and GitHub camo — no script execution needed. GitHub strips JS but renders SMIL. |
| Per-char `<tspan opacity="0">` with `begin` | Typewriter effect without reflows — each char just fades in at its `begin`. |
| `max_line` viewport + `y` chaining | Overflow lines trigger a `y` jump (`LINE_H = 20`) at their `begin`, so the terminal scrolls exactly like a real console. |
| `\x1b[<ms>p` delay escape | Lets a single output string pause mid-text (e.g. `"loading\x1b[400p done"`). Parsed into `Segment.delay`. |
| `svgwrite` writer | Keeps SVG generation explicit and tested; no string concatenation of XML. |
| No imports from `apps/` | The lib is usable in scripts, tests, and other projects; badge modules import *from* it, not vice versa. |

## Relationship to Badges

Each badge module builds a `COMMANDS: list[dict]` session script and calls:

```python
view = TerminalSVG(max_line=8)  # name: 8, console: 8, skills: 20
view.command_prefix = f"{GREEN}nova@ProjectNova:{BLUE}~{RESET}$ "
view.delay_per_char_input = 0.03
view.delay_per_char_output = 0.0
for entry in COMMANDS:
    view.add_line(entry)
return view.render()
```

See [SVG Badges](../svg-badges/index.md) for the three badge sessions.

## Testing

`tests/test_terminal_svg.py` covers:

- `parse_ansi` color/style/reset/delay (see [ANSI Parsing](ansi.md)).
- `TerminalSVG` rendering — `tspan`, `animate`, `freeze`, scroll, prefix, timing.
- Height scaling — `BODY_TOP(60) + max_line*20 + 6`.

Run: `pytest tests/test_terminal_svg.py -q`.
