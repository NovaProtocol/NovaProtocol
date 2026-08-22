"""Example: render an animated terminal session with the TerminalSVG class."""

from __future__ import annotations

import tempfile
import webbrowser

from utilities.terminal_svg import TerminalSVG

GREEN = "\x1b[32m"
BLUE = "\x1b[34m"
RED = "\x1b[31m"
YELLOW = "\x1b[33m"
GRAY = "\x1b[90m"
BOLD = "\x1b[1m"
RESET = "\x1b[0m"

view = TerminalSVG(max_line=10)
view.command_prefix = f"{GREEN}nova@ProjectNova:{BLUE}~{RESET}$ "

# Typing feel.
view.delay_per_char_input = 0.08
view.delay_per_char_output = 0.01

# A custom \x1b[<ms>p escape pauses mid-text to fake a slow command.
view.add_line(
    {
        "input": f"{RED}gerp -i error /var/log/app.log{RESET}",
        "output": [f"{RED}bash: gerp: command not found{RESET}"],
    }
)
view.add_line(
    {
        "input": "grep -i error /var/log/app.log",
        "output": [
            f"{RED}[2026-08-09 17:20:11] ERROR  api/main.py:42{RESET}",
            f"{YELLOW}[2026-08-09 17:20:09] WARN   api/routes.py:88{RESET}",
        ],
    }
)
view.add_line(
    {
        "input": "curl localhost/health",
        # \x1b[400p = 400ms "thinking" delay before the reply
        "output": [f'{GREEN}{BOLD}{{"status":"ok"}}{RESET}'],
        "delay": 0.4,
    }
)

if __name__ == "__main__":
    svg = view.render()
    with tempfile.NamedTemporaryFile(suffix=".svg", delete=False, mode="w") as tmp:
        tmp.write(svg)
        tmp_name = tmp.name
    print(f"Written to {tmp_name} ({len(svg)} bytes)")
    webbrowser.open(f"file://{tmp_name}")
