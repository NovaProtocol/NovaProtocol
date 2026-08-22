# Console Badge (`apps/console_svg.py`)

An 8-line “bring-up” badge — a fresh Linux boot, then the pre-prod `docker compose up` of this exact host (FastAPI + Caddy + Cloudflare Tunnel serving `github.projectnova.download`). The longest session; scrolls rapidly.

## Route

`GET /console.svg` → `image/svg+xml` with `Cache-Control: no-store, max-age=0` (`apps/routes.py::console_route`).

## Session Highlights

```python
# apps/console_svg.py — COMMANDS: list[dict] (abridged)

COMMANDS = [
    # SSH in (same PowerShell → password open as name.svg/cl skills)
    {"input": "ssh nova@ProjectNova.remote",  "custom_prefix": "PS C:\\Users\\khyles> ", ...},
    {"input": "************",                  "custom_prefix": "nova@ProjectNova.local's password: ", ...},

    # Host probes
    {"input": "whoami",                        "output": ["nova"]},
    {"input": "hostname",                      "output": ["prod-01"]},
    {"input": "uptime",                        "output": [" 10:24:01 up 0 min,  1 user,  load average: 0.85, 0.60, 0.25"]},
    {"input": "uname -a",                      "output": ["Linux prod-01 6.8.0-40-generic #40-Ubuntu SMP x86_64 GNU/Linux"]},
    {"input": "free -h",                       "output": [f"{BLUE}               total ...{RESET}", ...]},
    {"input": "df -h",                         "output": [f"{BLUE}Filesystem ...{RESET}", ...]},
    {"input": "ss -tlnp",                      "output": [f"{BLUE}State ...{RESET}", ...]},
    {"input": "systemctl --failed",            "output": [f"{GREEN}0 loaded units listed. Pass.{RESET}"]},

    # Compose dance
    {"input": "docker compose ps",             "output": [f"{BLUE}NAME ...{RESET}", "novaprotocol_main     (created) ..."]},
    {"input": "docker compose uo -d",          "output": [f"{RED}bash: uo: command not found{RESET}", "Usage:  docker compose ..."]},
    {"input": "docker compose up -d",          "output": [f"{GREEN}Container novaprotocol_main   Started{RESET}", ...]},
    {"input": "docker compose ps",             "output": [f"{BLUE}NAME ...{RESET}", "novaprotocol_main     novaprotocol/app:latest ..."]},

    # Logs + health
    {"input": "docker logs novaprotocol_main --tail 30",
     "output": [f"{GRAY}[INFO] Starting granian{RESET}", ...]},
    {"input": "curl -s localhost:7051/health", "output": [f"{GREEN}{{\"status\":\"ok\"}}{RESET}"]},

    # Tunnel + public
    {"input": "cloudflared tunnel list",       "output": [f"{BLUE}ID ...{RESET}", "2a3b4c5d-... novaprotocol ..."]},
    {"input": "curl -s https://github.projectnova.download/health",
     "output": [f"{GREEN}{{\"status\":\"ok\"}}{RESET}"]},

    {"input": "exit",                          "output": ["logout", "Connection to ProjectNova.remote closed."]},
    {"input": "", "output": [],                "custom_prefix": "PS C:\\Users\\khyles> "},  # trailing prompt
]
```

Key narrative beats:

- **Intentional typo** `docker compose uo -d` → `bash: uo: command not found` — drives the rendered error; the next line is the correction `up -d`.
- **Phase contrast** — `compose ps` before shows `created` vs after shows `Up 2 seconds`.
- **Granian logs** + **Caddy logs** + two `curl /health` (localhost vs tunnel) prove the whole chain.

## Renderer

```python
def render_console_svg(max_line: int = 8) -> str:
    view = TerminalSVG(max_line=max_line)
    view.command_prefix = f"{GREEN}nova@ProjectNova:{BLUE}~{RESET}$ "
    view.delay_per_char_input = 0.03
    view.delay_per_char_output = 0.0
    view.delay_per_line_input = 1
    view.delay_per_line_output = 0.05
    view.delay_after_entry = 0.05
    for entry in COMMANDS:
        view.add_line(entry)
    return view.render()
```

- `max_line=8` — same compact height as name badge (`226px`), so all three badges align in the profile grid.
- `delay_per_line_input=1` — prompt shows for a second before typing (breathing room between rapid commands).
- `delay_per_line_output=0.05` + `delay_after_entry=0.05` — output bursts but each line and each entry gets a 50ms beat so the scroll is readable.
- `max_line` is a param (default `8`) so tests can render with a different viewport if needed.

## Scrolling

`COMMANDS` yields far more than 8 `Row`s (every input + every output line). Overflow `begin` times trigger the renderer's `y` chain — with ~20 distinct rows, about 12 scroll jumps, each 20px, so the badge scrolls almost continuously. The viewer sees the last 8 rows settle (logs + health).

## Tests

`tests/test_console_svg.py`:

```python
def test_console_svg_has_chrome():
    out = render_console_svg()
    assert "nova@ProjectNova" in out
    assert "#0D1117" in out
```

`tests/test_routes.py::test_console_svg_route`:

```python
def test_console_svg_route():
    with TestClient(create_app()) as client:
        r = client.get("/console.svg")
        assert r.headers["content-type"].startswith("image/svg+xml")
        assert b"nova@ProjectNova" in r.content
```

When editing output strings, keep ANSI coloring consistent — `BLUE` headers, `GREEN` success, `RED` error, `GRAY` logs — so the profile render stays themed.
