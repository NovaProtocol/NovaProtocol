"""Skills badge — a terminal that runs intro scripts.

Each command's output fills the full max_line (20) rows, padded with blank
lines, and holds for 10s so it can be read before the next command scrolls in.
Only public, non-sensitive info (no contact/experience details).
"""

from __future__ import annotations

from utilities.terminal_svg import TerminalSVG

# ANSI helpers.
GREEN = "\x1b[32m"
BLUE = "\x1b[34m"
RED = "\x1b[31m"
YELLOW = "\x1b[33m"
CYAN = "\x1b[36m"
GRAY = "\x1b[90m"
BOLD = "\x1b[1m"
RESET = "\x1b[0m"

COMMANDS: list[dict] = [
    {
        "input": "ssh nova@ProjectNova.remote",
        "output": [],
        "custom_prefix": "PS C:\\Users\\khyles> ",
        "custom_end_delay": 1.5,
        "custom_start_delay": 1,
    },
    {
        "input": "************",
        "output": [],
        "custom_prefix": "nova@ProjectNova.local's password: ",
        "custom_end_delay": 3,
        "custom_start_delay": 1,
    },
    {
        "input": "./get_summary.sh",
        "output": [
            f"{GREEN}DOST Scholar · engineering student{RESET}",
            f"{BLUE}Backend Development {RESET}{RED  }RESTful APIs · SQL data models{RESET}",
            f"{BLUE}Frontend & Mobile   {RESET}{YELLOW}web apps · mobile apps{RESET}",
            f"{BLUE}DevOps              {RESET}{CYAN }Docker containers · reverse proxies · deployment{RESET}",
            f"{BLUE}Networking          {RESET}{GREEN}Cloudflare Tunnel · domains · infra{RESET}",
            f"{BLUE}Embedded & Hardware {RESET}{RED  }sensors · NFC · microcontrollers{RESET}",
            f"{BLUE}Mechanical          {RESET}{YELLOW}CAD modeling · 3D design{RESET}",
            "", "", "", "", "", "", "", "", "", "", "", "",
        ],
        "custom_start_delay": 0.5,
        "custom_end_delay": 10.0,
    },
    {
        "input": "./get_tech_stack.sh",
        "output": [
            f"{BLUE}Programming      {RESET}{RED   }Python · C++ · JavaScript · Rust · TypeScript · SQL{RESET}",
            f"{BLUE}Frameworks       {RESET}{YELLOW}Flask · FastAPI · Django · SQLAlchemy · Jinja2 · Bootstrap{RESET}",
            f"{BLUE}Databases        {RESET}{CYAN  }MySQL · SQLite{RESET}",
            f"{BLUE}Servers & Deploy {RESET}{GREEN }Node.js · Docker · Caddy · Nginx · Gunicorn · Granian · Debian{RESET}",
            f"{BLUE}Networking       {RESET}{RED   }Cloudflare Tunnel · Tailscale Funnel · Domain Management{RESET}",
            f"{BLUE}Mobile           {RESET}{YELLOW}React Native · Expo{RESET}",
            f"{BLUE}Hardware         {RESET}{CYAN  }Arduino · ESP32 · RP2040 · Raspberry Pi · STM32 · NTAG215{RESET}",
            f"{BLUE}Mechanical       {RESET}{GREEN }AutoCAD · OnShape · Fusion 360 · Cura{RESET}",
            "", "", "", "", "", "", "", "", "", "", "",
        ],
        "custom_start_delay": 0.5,
        "custom_end_delay": 10.0,
    },
    {
        "input": "./get_certification.sh",
        "output": [
            f"{BLUE}SO2             {RESET}{GREEN}DOLE Accredited Safety Officer 2 · BOSH · 2024{RESET}",
            "", "", "", "", "", "", "", "", "", "",
            "", "", "", "", "", "", "", "",
        ],
        "custom_start_delay": 0.5,
        "custom_end_delay": 10.0,
    },
    {
        "input": "./get_projects.sh",
        "output": [
            f"{RED  }Private{RESET} - {GREEN}{BOLD}GateKeeper{RESET}      {BLUE}SSO access-code auth gate · Flask · Docker{RESET}",
            f"{RED  }Private{RESET} - {GREEN}{BOLD}Portfolio{RESET}       {BLUE}Personal site · Flask · Gunicorn · Cloudflare Tunnel{RESET}",
            f"{RED  }Private{RESET} - {GREEN}{BOLD}Water Billing{RESET}   {BLUE}Utility CIS · FastAPI · MySQL · Xendit · Docker{RESET}",
            f"{RED  }Private{RESET} - {GREEN}{BOLD}SolveSpace{RESET}      {BLUE}Python practice sandbox · Flask · Bubblewrap{RESET}",
            f"{GREEN}Public {RESET} - {GREEN}{BOLD}NovaProtocol{RESET}    {BLUE}GitHub profile SVG asset server · FastAPI · svgwrite{RESET}",
            "", "", "", "", "", "", "", "", "", "", "", "", "", "",
        ],
        "custom_start_delay": 0.5,
        "custom_end_delay": 10.0,
    },
]


def render_skills_svg() -> str:
    view = TerminalSVG(max_line=20)
    view.command_prefix = f"{GREEN}nova@ProjectNova:{BLUE}~{RESET}$ "
    view.delay_per_char_input = 0.05
    view.delay_per_char_output = 0.0
    for entry in COMMANDS:
        view.add_line(entry)
    return view.render()
