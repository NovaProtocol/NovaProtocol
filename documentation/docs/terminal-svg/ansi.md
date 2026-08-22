# ANSI Parsing (`utilities/terminal_svg/ansi.py`)

Converts inline ANSI SGR escapes in entry strings into styled `Segment`s that the timeline and renderer can emit as colored `<tspan>`s.

## Palette

```python
BG = "#0D1117"  # terminal background (also in render.py chrome)
FG = "#c8d2dc"  # default foreground
GREEN = "#50c878"  # also ANSI 32
GREEN_DIM = "#3aa75f"
GRAY = "#828c9b"  # also ANSI 90
BLUE = "#6ea0eb"  # also ANSI 34
RED = "#ff5555"  # also ANSI 31
YELLOW = "#e6c85a"  # also ANSI 33
PINK = "#e678be"  # also ANSI 35
FONT = "DejaVu Sans Mono, Menlo, Consolas, monospace"

ANSI_FG = {
    "30": "#000000",
    "31": RED,
    "32": "#50c878",
    "33": YELLOW,
    "34": BLUE,
    "35": PINK,
    "36": "#8be9fd",
    "37": FG,
    "90": GRAY,
    "91": RED,
    "92": "#50c878",
    "93": YELLOW,
    "94": BLUE,
    "95": PINK,
    "96": "#8be9fd",
    "97": "#ffffff",
}
```

Only foreground SGR codes are supported — background SGR (`40`-`47`, `100`-`107`) is not needed for terminal badges. Add entries to `ANSI_FG` if a new color is needed; the renderer already copies `style.fg` verbatim into `fill`.

## Style

```python
@dataclass
class Style:
    fg: str = FG
    bold: bool = False
    italic: bool = False
    underline: bool = False
```

Bold/italic/underline map to `font-weight`, `font-style`, `text-decoration` in the rendered `<tspan>`.

## Segment

```python
@dataclass
class Segment:
    text: str
    style: Style
    delay: float = 0.0  # pause (seconds) before this segment's first char
```

`delay` is the custom pause escape (`\x1b[<ms>p`) accumulated before the segment — the timeline adds it to `t` before emitting the segment's chars. Example: `"loading\x1b[400p done"` → two segments, second with `delay=0.4`.

## Regexes

```python
_SGR = re.compile(r"\x1b\[([0-9;]*)m")  # e.g. \x1b[32m, \x1b[1;4m, \x1b[0m
_DELAY = re.compile(r"\x1b\[(\d+)p")  # e.g. \x1b[500p = 500ms pause
```

Tokens from both regexes are collected, sort-merged by start offset, then scanned left-to-right. Text between tokens becomes `Segment`s with the current `Style`; `delay` tokens accumulate into `delay_acc` and are attached to the *next* segment's `delay`.

## API

### `_apply_code(style, code)`

Mutates `style` for one SGR code:

| Code | Effect |
|------|--------|
| `0` or `""` | reset: fg→FG, bold/italic/underline→False |
| `1` | `bold=True` |
| `3` | `italic=True` |
| `4` | `underline=True` |
| `39` | `fg=FG` |
| `30`-`37`, `90`-`97` | `fg=ANSI_FG[code]` |

Unknown codes are ignored — add them to `ANSI_FG` or a new branch if needed. Multi-code SGRs like `\x1b[1;34m` are split on `;` and applied in order.

### `parse_ansi(text, base=None) -> list[Segment]`

Splits `text` on SGR and pause escapes. Escape codes are stripped; each returned `Segment` carries the style active *after* the preceding escapes and the pause before it.

```python
from utilities.terminal_svg import parse_ansi

parse_ansi("\x1b[32mhello\x1b[0m")
# -> [Segment("hello", Style(fg="#50c878"), 0.0)]

parse_ansi("\x1b[1;4mbold_underline\x1b[0m")
# -> [Segment("bold_underline", Style(bold=True, underline=True), 0.0)]

parse_ansi("ab\x1b[500pcd")
# -> [Segment("ab", ..., 0.0), Segment("cd", ..., 0.5)]

parse_ansi("plain")
# -> [Segment("plain", Style(), 0.0)]
```

`base` lets callers inherit a style (used internally for per-line base resets); default is a fresh `Style()`.

Edge cases:

- Empty `text` → `[Segment("", Style(), delay_acc)]` (keeps delay even if nothing renders).
- Consecutive escapes without text → no empty segments, delay accumulates.
- Unknown SGR → ignored; style unchanged.

## How Entry Strings Use It

Badge modules write entries with inline ANSI for readability:

```python
GREEN = "\x1b[32m"
RED = "\x1b[31m"
RESET = "\x1b[0m"

COMMANDS = [
    {"input": "whoami", "output": ["nova"]},
    {
        "input": "docker compose up -d",
        "output": [f"{GREEN}Container novaprotocol_main   Started{RESET}"],
    },
]
```

`build_timeline()` calls `parse_ansi(prefix)`, `parse_ansi(cmd)`, and `parse_ansi(out_line)` separately — prefix, input, and each output line get independent style tracks.

## Testing

`tests/test_terminal_svg.py::test_parse_ansi_*`:

```python
def test_parse_ansi_color():
    segs = parse_ansi("\x1b[32mhello\x1b[0m")
    assert segs[0].style.fg == "#50c878"


def test_parse_ansi_delay_code():
    segs = parse_ansi("ab\x1b[500pcd")
    assert segs[1].delay == 0.5
```

## Gotchas

- Input is forced white (`Style(fg=FG)`) in `build_timeline()` — what you type should not be pre-colored as if the shell already knew the outcome. Output keeps its parsed colors.
- The custom `\x1b[<ms>p` is **not** a standard SGR — it is a project-specific pause. It intentionally reuses the CSI prefix so it looks like an ANSI escape in the entry strings but is parsed separately by `_DELAY`.
- `, ".join` on ANSI_FG keys is not sorted — add new codes alphabetically for readability.
