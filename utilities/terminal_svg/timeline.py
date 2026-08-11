"""Timeline — turns entries into per-character events with begin times."""

from __future__ import annotations

from dataclasses import dataclass, field

from utilities.terminal_svg.ansi import FG, Segment, Style, parse_ansi


@dataclass
class Char:
    text: str
    style: Style
    begin: float  # seconds into the timeline when this char appears


@dataclass
class Row:
    """One rendered line: the command (prefix+input) or one output line."""

    chars: list[Char]
    begin: float  # when this row starts appearing
    kind: str = "output"  # "command" | "output"
    delay: float = 0.0    # per-entry pause (for slow commands)

    def __post_init__(self):
        if not self.chars and not hasattr(self, "_empty"):
            self.chars = []


@dataclass
class Timeline:
    rows: list[Row] = field(default_factory=list)
    total: float = 0.0


def build_timeline(
    entries: list[dict],
    command_prefix: str,
    delay_per_char_input: float,
    delay_per_char_output: float,
    delay_per_line_input: float,
    delay_per_line_output: float,
    delay_after_entry: float,
) -> Timeline:
    """Expand entries into per-char events. Returns the full timeline."""
    rows: list[Row] = []
    t = 0.0

    for entry in entries:
        cmd = str(entry.get("input") or "")
        entry_delay = float(entry.get("delay") or 0.0)

        # Per-entry overrides (default to the view-wide settings).
        prefix = str(entry.get("custom_prefix", command_prefix) or "")
        start_delay = float(entry.get("custom_start_delay", delay_per_line_input) or 0.0)
        end_delay = float(entry.get("custom_end_delay", delay_after_entry) or 0.0)

        # --- command row ---
        row_begin = t
        chars: list[Char] = []

        # prefix appears ~instantly
        for seg in parse_ansi(prefix):
            t += seg.delay
            for ch in seg.text:
                chars.append(Char(ch, seg.style, t))
                t += 0.001

        # start_delay: the prompt is already shown, we "think" before typing.
        t += start_delay

        # input types char by char (always white — what you type shouldn't be
        # pre-colored as if the shell already knew the outcome)
        for seg in parse_ansi(cmd):
            t += seg.delay
            white = Style(fg=FG)
            for ch in seg.text:
                chars.append(Char(ch, white, t))
                t += delay_per_char_input

        rows.append(Row(chars=chars, begin=row_begin, kind="command", delay=entry_delay))

        # --- output rows ---
        step = delay_per_char_output if delay_per_char_output > 0 else 0.001
        for out_line in entry.get("output", []):
            t += delay_per_line_output
            orow_begin = t
            ochars: list[Char] = []
            for seg in parse_ansi(str(out_line)):
                t += seg.delay
                for ch in seg.text:
                    ochars.append(Char(ch, seg.style, t))
                    t += step
            rows.append(Row(chars=ochars, begin=orow_begin, kind="output"))

        # end_delay + entry_delay land AFTER the whole entry (outputs included),
        # so the next command waits — like the shell sitting at the prompt.
        t += end_delay + entry_delay

    total = t + 1.0  # small settle at the end
    return Timeline(rows=rows, total=total)
