"""Per-project terminal badges, served for the portfolio and for README embeds.

Each badge is a short animated terminal session that shows what the project is and
what it does, rendered with the same `TerminalSVG` machinery as the profile
badges. The content is deliberately about behaviour rather than implementation:
a reader sees the project do its job instead of reading a technology list.

Badges are keyed by slug so a project page and a README can point at the same
asset.
"""

from __future__ import annotations

from utilities.terminal_svg import TerminalSVG

# ANSI helpers, matching the other badge modules.
RED = "\x1b[31m"
GREEN = "\x1b[32m"
YELLOW = "\x1b[33m"
BLUE = "\x1b[34m"
CYAN = "\x1b[36m"
GRAY = "\x1b[90m"
BOLD = "\x1b[1m"
RESET = "\x1b[0m"

# Each session is a list of (input, output) entries. Keep them short: a badge is
# read at a glance, and a long animation is worse than no animation.
SESSIONS: dict[str, list[dict]] = {
    "gatekeeper": [
        {
            "input": "curl -sI https://app.example.com/private",
            "output": [
                f"{YELLOW}HTTP/2 302{RESET}",
                "location: https://gate.app.example.com/login",
                f"{GRAY}no cookie, no access{RESET}",
            ],
        },
        {
            "input": "curl -sI https://app.example.com/private \\",
            "output": [
                f"{GRAY}  -H 'Cookie: gate=eyJhbGciOi...'{RESET}",
                "",
                f"{GREEN}HTTP/2 200{RESET}",
                f"{GRAY}signed cookie accepted, forwarding{RESET}",
            ],
        },
        {
            "input": "gatekeeper codes revoke --label recruiter",
            "output": [f"{GREEN}revoked{RESET} {GRAY}1 code, 3 apps signed out{RESET}"],
        },
    ],
    "water-billing-system": [
        {
            "input": "billing read --meter 10023 --value 1284",
            "output": [
                f"{GRAY}computing password on device, no network needed{RESET}",
                f"{GREEN}reading recorded{RESET} {GRAY}meter=10023 value=1284 m3{RESET}",
            ],
        },
        {
            "input": "billing compute --meter 10023 --period 2026-08",
            "output": [
                f"{GRAY}usage 22.1 m3 across 5 tariff tiers{RESET}",
                "billed_amount  PHP 463.00",
                "penalty        PHP   0.00",
            ],
        },
        {
            "input": "billing pay --meter 10023 --amount 500",
            "output": [
                f"{GREEN}applied to oldest unpaid first{RESET}",
                f"{GRAY}remaining 37.00 held as account credit{RESET}",
            ],
        },
    ],
    "mle-review": [
        {
            "input": "mle solve 'P = 2*pi*N*T/60'",
            "output": [
                f"{GRAY}dimensions checked, no unit mismatch{RESET}",
                "P = 2*pi*N*T/60",
            ],
        },
        {
            "input": "mle review --topic thermodynamics --count 5",
            "output": [
                f"{GREEN}5 questions{RESET} {GRAY}with worked solutions{RESET}",
                f"{GRAY}2 flagged for a second pass{RESET}",
            ],
        },
    ],
    "solvespace": [
        {
            "input": "./solvespace run solution.py --problem 1846C",
            "output": [
                f"{GRAY}entering sandbox: 1 GB cap, 25 s cpu, no network{RESET}",
                f"{GREEN}case 1 OK{RESET}  {GREEN}case 2 OK{RESET}  {RED}case 3 WA{RESET}",
                f"{GRAY}verdict: wrong answer on case 3{RESET}",
            ],
        },
        {
            "input": "./solvespace run solution.py --problem 1846C",
            "output": [
                f"{GREEN}case 1 OK{RESET}  {GREEN}case 2 OK{RESET}  {GREEN}case 3 OK{RESET}",
                f"{GREEN}accepted{RESET} {GRAY}3/3 cases, 0.31 s{RESET}",
            ],
        },
    ],
    "portfolio": [
        {
            "input": "./portfolio serve",
            "output": [
                f"{GREEN}projects  6{RESET} {GRAY}each with a live demo{RESET}",
                f"{GREEN}resume    rendered{RESET} {GRAY}from data, never stale{RESET}",
                f"{GRAY}behind GateKeeper like everything else{RESET}",
            ],
        },
    ],
    "novaprotocol": [
        {
            "input": "curl -s https://github.example.com/public/name.svg",
            "output": [
                f"{GRAY}<svg baseProfile=\"full\" ...{RESET}",
                f"{GREEN}animated svg rendered{RESET} {GRAY}on every page load{RESET}",
            ],
        },
    ],
}

DEFAULT_COMMAND_PREFIX = f"{GREEN}admin@{BLUE}projectnova{RESET}$ "


def render_project_badge(slug: str, max_line: int = 8) -> str:
    """Render the animated terminal badge for a project slug."""
    session = SESSIONS.get(slug)
    if session is None:
        raise KeyError(slug)

    view = TerminalSVG(max_line=max_line)
    view.command_prefix = DEFAULT_COMMAND_PREFIX
    view.delay_per_char_input = 0.03
    view.delay_per_char_output = 0.0
    for entry in session:
        view.add_line(entry)
    return view.render()


def slugs() -> list[str]:
    """Slugs with a badge, in a stable order."""
    return sorted(SESSIONS)
