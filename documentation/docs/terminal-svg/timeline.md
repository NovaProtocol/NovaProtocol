# Timeline Engine (`utilities/terminal_svg/timeline.py`)

Turns a session script (`list[dict]` entries) into a `Timeline` of per-character events with absolute `begin` times. The renderer then turns those events into SMIL `<animate>` tags.

## Data Types

```python
@dataclass
class Char:
    text: str
    style: Style
    begin: float  # seconds into the animation when this char appears


@dataclass
class Row:
    chars: list[Char]
    begin: float  # when this row starts appearing
    kind: str = "output"  # "command" | "output"


@dataclass
class Timeline:
    rows: list[Row] = field(default_factory=list)
    total: float = 0.0  # full duration + 1s settle
```

- `Char.begin` is the `opacity` animation `begin` for that `<tspan>` char.
- `Row.begin` is when the row's first char appears; overflow rows' `begin` also doubles as the scroll `y` jump time.
- `Timeline.total` is `t + 1.0` at the end — the extra second lets the last line linger before a looping build would restart.

## `build_timeline()`

```python
def build_timeline(
    entries: list[dict],
    command_prefix: str,
    delay_per_char_input: float,
    delay_per_char_output: float,
    delay_per_line_input: float,
    delay_per_line_output: float,
    delay_after_entry: float,
) -> Timeline:
```

Called by `TerminalSVG.render()` with the view's timing fields plus each entry's `custom_*` overrides.

### Entry Schema

```python
{
    "input": "ssh nova@ProjectNova.remote",  # str — what was typed (typed char-by-char)
    "output": ["nova", "prod-01"],  # list[str] — lines printed after
    "delay": 0.4,  # float — extra wait after entry (alt name)
    "custom_prefix": "PS C:\\Users\\khyles> ",  # override view.command_prefix for this entry
    "custom_start_delay": 1.0,  # override delay_per_line_input for this entry
    "custom_end_delay": 1.5,  # override delay_after_entry for this entry
}
```

- `input` may be `""` — then only the prompt shows (used for the final empty `PS ...>` prompt).
- `output` lines are typed with `delay_per_char_output` (or `0.001` if that is `0` — a tiny step so each char still gets a distinct `begin` for `tspan` splitting).
- ANSI colors in `input` are parsed but **forced white** (`Style(fg=FG)`) — see [ANSI Parsing](ansi.md).
- `custom_prefix` without a trailing space is allowed; `build_timeline()` parses the whole string.

### Timing

```
t = 0.0
for entry in entries:
    prefix = entry.custom_prefix or command_prefix
    start_delay = entry.custom_start_delay or delay_per_line_input
    end_delay   = entry.custom_end_delay   or delay_after_entry

    # command row
    row_begin = t
    for seg in parse_ansi(prefix):
        t += seg.delay
        for ch in seg.text:
            chars.append(Char(ch, seg.style, t))
            t += 0.001                # prefix appears ~instantly (1ms per char)

    t += start_delay                  # prompt visible, "thinking" before typing

    for seg in parse_ansi(entry.input):
        t += seg.delay
        white = Style(fg=FG)
        for ch in seg.text:
            chars.append(Char(ch, white, t))
            t += delay_per_char_input # typing feel for input

    rows.append(Row(chars, row_begin, "command"))

    # output rows
    step = delay_per_char_output or 0.001
    for out_line in entry.output:
        t += delay_per_line_output
        orow_begin = t
        for seg in parse_ansi(out_line):
            t += seg.delay
            for ch in seg.text:
                ochars.append(Char(ch, seg.style, t))
                t += step             # output types (or bursts if step tiny)
        rows.append(Row(ochars, orow_begin, "output"))

    t += end_delay + entry.delay      # wait before next entry

total = t + 1.0
```

Key properties:

- `row_begin` is recorded *before* typing that row's chars — so the row's scroll `y` chain will fire exactly when the row starts appearing.
- `t` is monotonically increasing — `begin` values are globally sorted, which is why the renderer can derive scroll times as `rows[max_line:].begin`.
- `0.001` sentinel: prefix per-char step and empty-output step are not perceptible but give each char a unique `begin` for per-`tspan` `<animate>` granularity.

### Scrolling

The renderer does not decide when to scroll — the timeline does, implicitly: any `Row` beyond `max_line` (index `>= max_line`) contributes its `begin` to `scroll_times`. At that second, every row's `y` jumps up by `LINE_H` (20px). See [Rendering](render.md) for how `scroll_times` becomes `<animate attributeName="y">` chains.

Example: `max_line=8`, 12 rows total → rows 8, 9, 10, 11's `begin` are scroll events — 4 shifts, the viewport ends showing the last 8 rows.

## Example Timeline

```python
from utilities.terminal_svg import TerminalSVG

v = TerminalSVG(max_line=5)
v.command_prefix = "prompt:$ "
v.delay_per_char_input = 0.05
v.delay_per_line_input = 0.5
v.add_line({"input": "ls", "output": ["file.txt"]})

tl = v.render_timeline()  # if exposed, or inspect Timeline.rows directly
# tl.rows[0] -> kind="command", chars for "prompt:$ l","s", begin=0.0
# tl.rows[1] -> kind="output",  chars for "file.txt",          begin~0.5+2*0.05
# tl.total   -> last t + 1.0
```

More realistic (badge-style):

```python
view = TerminalSVG(max_line=8)
view.command_prefix = "\x1b[32mnova@ProjectNova:\x1b[34m~\x1b[0m$ "
view.delay_per_char_input = 0.03
view.add_line(
    {
        "input": "ssh nova@ProjectNova.remote",
        "output": [],
        "custom_prefix": "PS C:\\Users\\khyles> ",
        "custom_start_delay": 1.0,
        "custom_end_delay": 1.5,
    }
)
# → 1 prompt row (PS ...> + ssh ...) with 1s start delay and 1.5s end delay
#   no output rows, but the delays still advance t so the next command waits.
```

## Testing Timing

`tests/test_terminal_svg.py` asserts ordering, not wall-clock:

```python
# prefix shows at 0, input waits for custom_start_delay
prefix_begin = float(re.search(r'<tspan[^>]*>r<animate[^>]*begin="([0-9.]+)s"', svg).group(1))
input_begin = float(re.search(r'<tspan[^>]*>l<animate[^>]*begin="([0-9.]+)s"', svg).group(1))
assert prefix_begin == 0.0
assert input_begin >= 1.0
```

Read `svg.tostring()` and pull `begin="…s"` from `<animate>` — that is the observable contract. Don't assert on `Timeline.total` directly unless you freeze all delays.

## Gotchas

- `delay_per_char_output = 0.0` does **not** mean all output chars share one `begin` — the code uses `0.001` as the step, so each char still gets its own `tspan` with a 1ms stagger. Use a larger value for a visible typewriter on output.
- Empty `input` (`""`) still emits a prompt row — just the prefix, no typing delay. Used for the trailing `PS ...>` sentinel so the SVG ends on a live prompt.
- `entry["delay"]` and `custom_end_delay` **stack** (`t += end_delay + entry_delay`) — use one or the other, or be aware they add. Console badge uses `custom_end_delay` exclusively; `delay` is the legacy `__main__.py` demo path.
