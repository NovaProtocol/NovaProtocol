# Core API (`utilities/terminal_svg/core.py`)

The public facade — what badge modules and `__main__.py` actually import.

## Class `TerminalSVG`

```python
from utilities.terminal_svg import TerminalSVG

view = TerminalSVG(max_line: int = 14) -> None
```

### Fields

| Field | Type | Default | Meaning |
|-------|------|---------|---------|
| `command_prefix` | `str` | `"nova@ProjectNova:~$ "` | Prompt shown before every typed `input` (ANSI escapes allowed). Overridden per entry by `custom_prefix`. |
| `max_line` | `int` | constructor arg | Rows visible in the clipped viewport. Overflow rows cause scrolling. |
| `delay_per_char_input` | `float` | `0.08` | Seconds per input char typed. Badge overrides: `0.03` (name/console) / `0.05` (skills). |
| `delay_per_char_output` | `float` | `0.0` | Seconds per output char. `0.0` → bursts at `0.001` per char. |
| `delay_per_line_input` | `float` | `0.0` | Wait before typing input after prompt appears. Per-entry `custom_start_delay` overrides. |
| `delay_per_line_output` | `float` | `0.0` | Wait before each output line appears. |
| `delay_after_entry` | `float` | `0.0` | Wait after command+output before next entry. Per-entry `custom_end_delay` overrides. |
| `width` | `int` | `880` | SVG viewBox width. Override per-render with `render(width=…)`. |
| `loop` | `bool` | `False` | SMIL looping mode (see [Rendering](render.md)). |
| `_entries` | `list[dict]` | `[]` | Session script — mutated only via `add_line()` / `clear()`. |

### Methods

#### `add_line(entry: dict) -> None`

Append a session entry. Shape:

```python
{
    "input": str,  # typed command
    "output": list[str],  # lines printed after
    "delay": float,  # extra post-entry wait (legacy)
    "custom_prefix": str,  # prompt for this entry only
    "custom_start_delay": float,
    "custom_end_delay": float,
}
```

Only `input` and `output` are required — others default to the view's fields. `input` and each `output` line may contain ANSI escapes (`\x1b[32m`, `\x1b[90m`, …) and the custom pause `\x1b[<ms>p`.

```python
view.add_line({"input": "whoami", "output": ["nova"]})
view.add_line({"input": "", "output": [], "custom_prefix": "PS C:\\> "})  # trailing prompt
```

Re-read the entry schema in [Timeline Engine](timeline.md) for full defaults.

#### `clear() -> None`

Reset `self._entries = []`. Does not reset timing fields or `command_prefix`.

```python
view.clear()
view.add_line({"input": "ls", "output": ["a.txt"]})
```

#### `render(width: int | None = None) -> str`

Build the timeline and render the SVG string.

```python
svg: str = view.render()  # 880-wide, height = BODY_TOP + max_line*LINE_H + 6
svg: str = view.render(width=900)  # override width for this render only
```

Equivalent to:

```python
from utilities.terminal_svg.timeline import build_timeline
from utilities.terminal_svg.render import render_svg

timeline = build_timeline(
    self._entries,
    self.command_prefix,
    self.delay_per_char_input,
    self.delay_per_char_output,
    self.delay_per_line_input,
    self.delay_per_line_output,
    self.delay_after_entry,
)
return render_svg(timeline, max_line=self.max_line, width=width or self.width, loop=self.loop)
```

The SVG string is ready to serve:

```python
from fastapi.responses import Response

return Response(
    content=view.render(),
    media_type="image/svg+xml",
    headers={"Cache-Control": "no-store, max-age=0"},
)
```

## Re-exports

`utilities/terminal_svg/__init__.py` re-exports the palette and parser for convenience:

```python
from utilities.terminal_svg import (
    TerminalSVG,  # core
    Style,
    parse_ansi,  # ansi
    ANSI_FG,
    BG,
    BLUE,
    FONT,
    GRAY,
    GREEN,
    GREEN_DIM,
    PINK,
    RED,
    YELLOW,
)
```

Badge modules use the color names directly:

```python
from utilities.terminal_svg import TerminalSVG

GREEN = "\x1b[32m"
RESET = "\x1b[0m"
```

Utilities tests import `parse_ansi` and the color constants via this surface.

## Usage in Badges

Each badge module is the same pattern tuned for its session length:

```python
# apps/name_svg.py
def render_name_svg() -> str:
    view = TerminalSVG(max_line=8)
    view.command_prefix = f"{GREEN}nova@ProjectNova:{BLUE}~{RESET}$ "
    view.delay_per_char_input = 0.03
    view.delay_per_char_output = 0.0
    for entry in COMMANDS:
        view.add_line(entry)
    return view.render()


# apps/console_svg.py
def render_console_svg(max_line: int = 8) -> str: ...


# apps/skills_svg.py
def render_skills_svg() -> str:
    view = TerminalSVG(max_line=20)
    view.command_prefix = f"{GREEN}nova@ProjectNova:{BLUE}~{RESET}$ "
    view.delay_per_char_input = 0.05
    for entry in COMMANDS:
        view.add_line(entry)
    return view.render()
```

Only `max_line` and `delay_per_char_input` vary meaningfully — console and name share `8` (compact badge), skills uses `20` (tall cards with blank padding).

## `__all__`

```python
__all__ = [
    "TerminalSVG",
    "Style",
    "parse_ansi",
    "ANSI_FG",
    "BG",
    "BLUE",
    "GREEN",
    "GREEN_DIM",
    "GRAY",
    "RED",
    "YELLOW",
    "PINK",
    "FONT",
]
```

`BG`, `FONT`, etc. are re-exported so badge modules and tests can assert on palette without importing `ansi.py` directly.

## Testing

`tests/test_terminal_svg.py` exercises the facade without touching `apps/`:

```python
def test_terminal_svg_renders_last_max_lines():
    v = TerminalSVG(max_line=3)
    for i in range(5):
        v.add_line({"input": f"cmd{i}", "output": [f"out{i}"]})
    svg = v.render()
    assert svg.startswith("<svg")


def test_terminal_svg_custom_prefix_and_delays():
    v = TerminalSVG(max_line=5)
    v.command_prefix = "default:~$ "
    v.add_line(
        {
            "input": "ls",
            "output": ["file"],
            "custom_prefix": "root@box:~# ",
            "custom_start_delay": 1.0,
            "custom_end_delay": 0.5,
        }
    )
    svg = v.render()
    # prefix chars present, input waits for start_delay ...
```

Badge smoke tests call `render_*_svg()` directly (`tests/test_name_svg.py`, `tests/test_console_svg.py`) and assert `startswith("<svg")`.

## Gotchas

- `command_prefix` is parsed as ANSI — if you embed `\x1b[32m` in it, the prompt itself is colored. Badge modules set it to `f"{GREEN}nova@…:{BLUE}~{RESET}$ "` so the user/host is green, tilde is blue.
- `delay_per_char_input` is per **displayed** char after ANSI stripping — a long escape like `\x1b[34m` adds `delay` via its `Segment.delay` but no typing delay.
- `width` on the view is the default; `render(width=…)` is a per-call override that does not mutate `self.width`. Useful for tests (`render(width=600)`).
- `loop` is a field, not a `render()` arg — set `view.loop = True` before `render()`.
