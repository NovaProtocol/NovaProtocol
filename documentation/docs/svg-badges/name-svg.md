# Name Badge (`apps/name_svg.py`)

A compact 8-line badge — a terminal that SSHes in and runs `./introduce_yourself.sh`, showing green NOVA block art plus name and GitHub link.

## Route

`GET /name.svg` → `image/svg+xml` with `Cache-Control: no-store, max-age=0` (`apps/routes.py::name_route`).

## Session

```python
# apps/name_svg.py

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
```

- `max_line=8` — compact badge height `60 + 8*20 + 6 = 226` (viewBox `880×226`).
- `custom_prefix` on the first two entries fakes a Windows PowerShell → Linux password transition before the familiar `nova@ProjectNova:~$` prompt.
- `NOVA_ART` is 6 lines of `██` block art (46 chars/line) colored green via `\x1b[32m` — spacing assumes monospace `DejaVu Sans Mono`.
- The link `> https://github.com/NovaProtocol` is blue (`\x1b[34m`) so it reads as a hyperlink even inside the terminal.

## Timing

- `ssh` input types at 30ms/char, 1s start delay (prompt shows), 1.5s end delay (auth "thinking").
- Password dots (`************`) same, 2.5s end delay (feels like server response).
- `./introduce_yourself.sh` at 30ms/char, 0.5s start delay — then 6 green art lines + 2 text lines appear (output bursts at ~1ms/char).

Total wall-clock ≈ `ssh` typing + 1.5s + password typing + 2.5s + script typing + art/burst.

## Preview

Embed or fetch directly:

```html
<object type="image/svg+xml" data="/name.svg" style="max-width:100%;"></object>
```

Or `curl -s http://127.0.0.1:8000/name.svg | head -c 200`.

## Tests

`tests/test_name_svg.py`:

```python
def test_name_svg_renders():
    svg = render_name_svg()
    assert svg.startswith("<svg")
    assert "Khyles" in svg
```

`tests/test_routes.py::test_name_svg_route` hits the HTTP route:

```python
def test_name_svg_route():
    with TestClient(create_app()) as client:
        r = client.get("/name.svg")
        assert r.headers["content-type"].startswith("image/svg+xml")
        assert r.headers["cache-control"] == "no-store, max-age=0"
        assert b"Khyles" in r.content
```

When editing `NOVA_ART` or output lines, keep at least one stable assertion string (e.g. `"Khyles"` or a line fragment) so the route test still pins the contract.
