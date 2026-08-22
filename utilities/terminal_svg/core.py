"""TerminalSVG — public API for building animated terminal SVGs."""

from __future__ import annotations

from utilities.terminal_svg.render import render_svg
from utilities.terminal_svg.timeline import build_timeline


class TerminalSVG:
    """Renders a rolling terminal window as an animated SVG.

    Usage::

        view = TerminalSVG(max_line=14)
        view.command_prefix = "nova@ProjectNova:~$ "
        view.delay_per_char_input = 0.08
        view.add_line({"input": "ls", "output": ["file.txt"]})
        svg = view.render()
    """

    def __init__(self, max_line: int = 14) -> None:
        self.command_prefix = "nova@ProjectNova:~$ "
        self.max_line = int(max_line)

        # Typing feel (seconds)
        self.delay_per_char_input = 0.08
        self.delay_per_char_output = 0.0

        # Line timing (seconds, per entry):
        self.delay_per_line_input = 0.0  # wait before typing the input (prompt shows first)
        self.delay_per_line_output = 0.0  # wait before each output line appears
        self.delay_after_entry = 0.0  # wait after command+output before the next entry

        self.width = 880
        self._entries: list[dict] = []

        # Looping (keyTimes-based; may not render in some browsers)
        self.loop = False

    def add_line(self, entry: dict) -> None:
        """Append a line entry: ``{"input", "output": [...], "delay": s}``."""
        self._entries.append(entry)

    def clear(self) -> None:
        self._entries = []

    def render(self, width: int | None = None) -> str:
        if width is None:
            width = self.width

        timeline = build_timeline(
            self._entries,
            self.command_prefix,
            self.delay_per_char_input,
            self.delay_per_char_output,
            self.delay_per_line_input,
            self.delay_per_line_output,
            self.delay_after_entry,
        )
        return render_svg(
            timeline,
            max_line=self.max_line,
            width=width,
            loop=self.loop,
        )
