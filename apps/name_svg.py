"""Name badge — a terminal that SSHes in and runs ./introduce_yourself.sh.

Same pattern as apps/console_svg.py — builds a TerminalSVG session from a
COMMANDS list and returns the SVG string.
"""

from __future__ import annotations

from utilities.terminal_svg import TerminalSVG

# ANSI escape helpers (same pattern as apps/console_svg.py).
GREEN = "\x1b[32m"
BLUE = "\x1b[34m"
RESET = "\x1b[0m"

# Colored NOVA block art (46 chars per line, monospace-aligned).
NOVA_ART = [
    "███╗   ██╗   ██████╗   ██╗   ██╗   █████╗ ",
    "████╗  ██║  ██╔═══██╗  ██║   ██║  ██╔══██╗",
    "██╔██╗ ██║  ██║   ██║  ██║   ██║  ███████║",
    "██║╚██╗██║  ██║   ██║  ╚██╗ ██╔╝  ██╔══██║",
    "██║ ╚████║  ╚██████╔╝   ╚████╔╝   ██║  ██║",
    "╚═╝  ╚═══╝   ╚═════╝     ╚═══╝    ╚═╝  ╚═╝",
]

COMMANDS: list[dict] = [
    {
        "input": "ssh nova@ProjectNova.remote",
        "output": [],
        "custom_prefix": "PS C:\\Users\\khyles> ",
        "custom_start_delay": 1,
        "custom_end_delay": 1.5,
    },
    {
        "input": "************",
        "output": [],
        "custom_prefix": "nova@ProjectNova.local's password: ",
        "custom_start_delay": 1,
        "custom_end_delay": 2.5,
    },
    {
        "input": "./introduce_yourself.sh",
        "output": [
            *[f"{GREEN}{line}{RESET}" for line in NOVA_ART],
            "> Khyles Gibrian Ramos",
            f"{BLUE}> https://github.com/NovaProtocol{RESET}",
        ],
        "custom_start_delay": 0.5,
    },
]


def render_name_svg() -> str:
    view = TerminalSVG(max_line=8)
    view.command_prefix = f"{GREEN}nova@ProjectNova:{BLUE}~{RESET}$ "
    view.delay_per_char_input = 0.03
    view.delay_per_char_output = 0.0
    for entry in COMMANDS:
        view.add_line(entry)
    return view.render()
