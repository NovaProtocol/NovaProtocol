"""Per-project terminal badges, served for README embeds and the portfolio.

Each badge is a short animated terminal session that runs `./get_project_name.sh`
and prints the project name as ANSI Shadow block art, followed by a one-line
summary of what the project does. The art comes from the bundled FIGlet font
(`apps/fonts/ansi_shadow.flf`) via `apps.figlet`, so a new project is a name and
a sentence rather than a hand-drawn block of characters.

The route is `/public/project/<slug>.svg`.
"""

from __future__ import annotations

from apps import figlet
from utilities.terminal_svg import TerminalSVG

# ANSI helpers, matching the other badge modules.
GREEN = "\x1b[32m"
BLUE = "\x1b[34m"
CYAN = "\x1b[36m"
GRAY = "\x1b[90m"
RESET = "\x1b[0m"

# Every slug the route will answer for.
SLUGS: tuple[str, ...] = (
    "gatekeeper",
    "water-billing-system",
    "mle-review",
    "solvespace",
    "portfolio",
    "novaprotocol",
)

# What each badge prints. `art` is the name rendered in the block font, `blurb`
# is the one line under it, and `detail` is the muted second line.
PROJECTS: dict[str, dict[str, str]] = {
    "gatekeeper": {
        "art": "GateKeeper",
        "url": "https://gatekeeper.projectnova.download",
        "blurb": "one login for a family of self-hosted web apps",
    },
    "water-billing-system": {
        "art": "Water Billing",
        "url": "https://water-billing-system.projectnova.download",
        "blurb": "utility billing, from the meter reading to the receipt",
    },
    "mle-review": {
        "art": "MELE Review",
        "url": "https://melereview.projectnova.download",
        "blurb": "a study companion for the licensure exam",
    },
    "solvespace": {
        "art": "SolveSpace",
        "url": "https://solver.projectnova.download",
        "blurb": "a private competitive-programming practice workspace",
    },
    "portfolio": {
        "art": "Portfolio",
        "url": "https://portfolio.projectnova.download",
        "blurb": "the site that shows the rest of these projects",
    },
    "novaprotocol": {
        "art": "NovaProtocol",
        "url": "https://github.projectnova.download",
        "blurb": "a dynamic profile asset server",
    },
}

DEFAULT_COMMAND_PREFIX = f"{GREEN}nova@ProjectNova:{BLUE}~{RESET}$ "


def render_project_badge(slug: str, max_line: int = 8) -> str:
    """Render the animated terminal badge for a project slug.

    Mirrors `name_svg.render_name_svg`: the same ssh-and-password preamble, then
    one script whose output fills the terminal exactly.

    The line arithmetic is the whole trick and it is not negotiable. The session
    runs three prompt lines and eight output lines through an eight-row viewport,
    so the three prompts scroll away and the eight output lines come to rest
    filling it. That is what `name.svg` does, and it is why the art lands in
    frame instead of being cut.

    The font draws seven rows and the last is the empty baseline that gives the
    block letters their shadow, so only the six carved rows are emitted. Six
    carved rows plus the name and the link is eight, which is exactly `max_line`.

    Raises `KeyError` for an unknown slug so the route can answer `404`.
    """
    project = PROJECTS[slug]
    # Drop the blank baseline: it costs a row the terminal does not have.
    art = [line for line in figlet.render(project["art"]) if line.strip()]

    view = TerminalSVG(max_line=max_line)
    view.command_prefix = DEFAULT_COMMAND_PREFIX
    view.delay_per_char_input = 0.03
    view.delay_per_char_output = 0.0

    # Same preamble as name.svg. These prompt lines scroll off the top.
    view.add_line(
        {
            "input": "ssh nova@ProjectNova.remote",
            "output": [],
            "custom_prefix": "PS C:\\Users\\khyles> ",
            "custom_start_delay": 1,
            "custom_end_delay": 1.5,
        }
    )
    view.add_line(
        {
            "input": "************",
            "output": [],
            "custom_prefix": "nova@ProjectNova.local's password: ",
            "custom_start_delay": 1,
            "custom_end_delay": 2.5,
        }
    )
    view.add_line(
        {
            "input": "./get_project_name.sh",
            "output": [
                *[f"{CYAN}{line}{RESET}" for line in art],
                f"{GREEN}> {project['url']}{RESET}",
                f"{GRAY}> {project['blurb']}{RESET}",
            ],
            "custom_start_delay": 0.5,
        }
    )
    return view.render()


def slugs() -> list[str]:
    """Slugs with a badge, in a stable order."""
    return sorted(SLUGS)
