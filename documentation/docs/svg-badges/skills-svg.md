# Skills Badge (`apps/skills_svg.py`)

A tall 20-line badge — the “career panel” that cycles through four panes via `./get_*.sh` scripts, each full-screen (20 rows) × 10 seconds, padded with blank lines so the next pane scrolls in cleanly.

## Route

`GET /skills.svg` → `image/svg+xml` with `Cache-Control: no-store, max-age=0` (`apps/routes.py::skills_route`).

## Session

```python
# apps/skills_svg.py

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
            f"{BLUE}Backend Development {RESET}{RED}RESTful APIs · SQL data models{RESET}",
            f"{BLUE}Frontend & Mobile   {RESET}{YELLOW}web apps · mobile apps{RESET}",
            # … 7 content lines …
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",  # pad to 20
        ],
        "custom_start_delay": 0.5,
        "custom_end_delay": 10.0,
    },
    {
        "input": "./get_tech_stack.sh",
        "output": [
            f"{BLUE}Programming      {RESET}{RED}Python · C++ · JavaScript · Rust · TypeScript · SQL{RESET}",
            # … 8 content lines …
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ],
        "custom_start_delay": 0.5,
        "custom_end_delay": 10.0,
    },
    {
        "input": "./get_certification.sh",
        "output": [
            f"{BLUE}SO2             {RESET}{GREEN}DOLE Accredited Safety Officer 2 · BOSH · 2024{RESET}",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
        ],
        "custom_start_delay": 0.5,
        "custom_end_delay": 10.0,
    },
    {
        "input": "./get_projects.sh",
        "output": [
            f"{RED}Private{RESET} - {GREEN}{BOLD}GateKeeper{RESET}      {BLUE}SSO access-code auth gate · Flask · Docker{RESET}",
            f"{RED}Private{RESET} - {GREEN}{BOLD}Portfolio{RESET}       {BLUE}Personal site · Flask · Gunicorn · Cloudflare Tunnel{RESET}",
            f"{RED}Private{RESET} - {GREEN}{BOLD}Water Billing{RESET}   {BLUE}Utility CIS · FastAPI · MySQL · Xendit · Docker{RESET}",
            f"{RED}Private{RESET} - {GREEN}{BOLD}SolveSpace{RESET}      {BLUE}Python practice sandbox · Flask · Bubblewrap{RESET}",
            f"{GREEN}Public {RESET} - {GREEN}{BOLD}NovaProtocol{RESET}    {BLUE}GitHub profile SVG asset server · FastAPI · svgwrite{RESET}",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
            "",
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
```

### Pane Details

| Script | Lines (non-blank) | Content |
|--------|-------------------|---------|
| `get_summary.sh` | 7 | DOST scholar, backend, frontend/mobile, devops, networking, embedded, mechanical |
| `get_tech_stack.sh` | 8 | programming langs, frameworks, DBs, servers, networking, mobile, hardware, mechanical |
| `get_certification.sh` | 1 | SO2 — DOLE Accredited Safety Officer 2 · BOSH · 2024 |
| `get_projects.sh` | 5 | GateKeeper / Portfolio / Water Billing / SolveSpace / NovaProtocol with labels |

Each `output` is exactly `max_line` (20) rows — content + blank `""` padding. Blank output lines still generate a `Row` (empty `<text>`), so the timeline has uniform 20-row panes and the renderer's `y` chain scrolls one full viewport per pane.

### Timing

- `custom_start_delay=0.5` — short prompt beat before each script types.
- `custom_end_delay=10.0` — hold the pane for 10 seconds so the profile viewer can read before the next pane scrolls in. GitHub's camo cache is `no-store`, but the SVG itself still plays for ~40s before settling.

### Renderer

`max_line=20` → height `60 + 20*20 + 6 = 466` (viewBox `880×466`) — tallest badge, stands out in the profile's vertical stack.

`delay_per_char_input=0.05` — slightly slower than name/console (0.03) because these prompts are read as headings.

## Preview

```html
<object type="image/svg+xml" data="/skills.svg" style="max-width:100%;"></object>
```

Locally: `http://127.0.0.1:7051/test` shows the 466px pane with scroll.

## Tests

`tests/test_routes.py::test_skills_svg_route`:

```python
def test_skills_svg_route():
    with TestClient(create_app()) as client:
        r = client.get("/skills.svg")
        assert r.headers["content-type"].startswith("image/svg+xml")
        assert b"Python" in r.content  # tech stack pane
        assert b"GateKeeper" in r.content  # projects pane
```

When editing pane strings, keep at least one searchable token per pane stable (`"Python"`, `"GateKeeper"`, `"SO2"`) so the route test remains meaningful.

## Privacy Note

Only public, non-sensitive info — no contact, experience dates, or private URLs. See the module docstring: “Only public, non-sensitive info (no contact/experience details).”
