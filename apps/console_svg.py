from __future__ import annotations

from utilities.terminal_svg import TerminalSVG

# ANSI helpers so the command/output data below stays readable.
RED = "\x1b[31m"
GREEN = "\x1b[32m"
YELLOW = "\x1b[33m"
BLUE = "\x1b[34m"
GRAY = "\x1b[90m"
BOLD = "\x1b[1m"
RESET = "\x1b[0m"


# Inline ANSI codes let each command/output be a plain string.
# A fresh Linux boot, then the pre-prod bring-up of this exact host
# (FastAPI app + caddy + cloudflared serving github.projectnova.download).
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
        "input": "whoami",
        "output": ["nova"],
    },
    {
        "input": "hostname",
        "output": ["prod-01"],
    },
    {
        "input": "uptime",
        "output": [" 10:24:01 up 0 min,  1 user,  load average: 0.85, 0.60, 0.25"],
    },
    {
        "input": "uname -a",
        "output": ["Linux prod-01 6.8.0-40-generic #40-Ubuntu SMP x86_64 GNU/Linux"],
    },
    {
        "input": "free -h",
        "output": [
            f"{BLUE}               total  used    free   shared  buff/cache  available{RESET}",
            " Mem:           15Gi  1.2Gi   12Gi    112Mi    1.8Gi       13Gi",
            "Swap:          2.0Gi    0B   2.0Gi",
        ],
    },
    {
        "input": "df -h",
        "output": [
            f"{BLUE}Filesystem      Size  Used Avail Use% Mounted on{RESET}",
            "/dev/sda1       100G   38G   62G  38% /",
            "tmpfs           3.1G  1.2M  3.1G   1% /dev/shm",
        ],
    },
    {
        "input": "ss -tlnp",
        "output": [
            f"{BLUE}State   Recv-Q  Send-Q  Local Address:Port  Peer Address:Port  Process{RESET}",
            'LISTEN  0       4096    127.0.0.53:53        0.0.0.0:*          users:(("systemd-resolve",pid=389,fd=17))',
            'LISTEN  0       128     0.0.0.0:22           0.0.0.0:*          users:(("sshd",pid=412,fd=3))',
        ],
    },
    {
        "input": "systemctl --failed",
        "output": [f"{GREEN}0 loaded units listed. Pass.{RESET}"],
    },
    {
        "input": "docker compose ps",
        "output": [
            f"{BLUE}NAME                  IMAGE       STATUS          NAMES{RESET}",
            "novaprotocol_main     (created)                   novaprotocol_main",
            "novaprotocol_caddy    (created)                   novaprotocol_caddy",
        ],
    },
    {
        "input": "docker compose uo -d",  # "uo" typo is intentional: it drives the rendered error below
        "output": [
            f"{RED}bash: uo: command not found{RESET}",
            "Usage:  docker compose [OPTIONS] COMMAND",
        ],
    },
    {
        "input": "docker compose up -d",
        "output": [
            f"{GREEN}Container novaprotocol_main   Started{RESET}",
            f"{GREEN}Container novaprotocol_caddy  Started{RESET}",
        ],
    },
    {
        "input": "docker compose ps",
        "output": [
            f"{BLUE}NAME                  IMAGE                     STATUS           NAMES{RESET}",
            "novaprotocol_main     novaprotocol/app:latest   Up 2 seconds     novaprotocol_main",
            "novaprotocol_caddy    caddy:2-alpine            Up 2 seconds     novaprotocol_caddy",
        ],
    },
    {
        "input": "docker logs novaprotocol_main --tail 30",
        "output": [
            f"{GRAY}[INFO] Starting granian{RESET}",
            f"{GRAY}[INFO] Interface: asgi{RESET}",
            f"{GRAY}[INFO] Host: 0.0.0.0{RESET}",
            f"{GRAY}[INFO] Port: 7051{RESET}",
            f"{GRAY}[INFO] Worker count: 1{RESET}",
            f"{GRAY}[INFO] Spawning worker process 1{RESET}",
            f"{GREEN}[INFO] Application startup complete.{RESET}",
        ],
    },
    {
        "input": "docker logs novaprotocol_caddy --tail 20",
        "output": [
            f'{GRAY}{{"level":"info","logger":"admin","msg":"admin endpoint started"}}{RESET}',
            f'{GRAY}{{"level":"info","logger":"http","msg":"server started","server_name":"srv0"}}{RESET}',
            f'{GRAY}{{"level":"info","logger":"http","msg":"serving initial configuration"}}{RESET}',
        ],
    },
    {
        "input": "curl -s localhost:7051/health",
        "output": [f'{GREEN}{{"status":"ok"}}{RESET}'],
    },
    {
        "input": "cloudflared tunnel list",
        "output": [
            f"{BLUE}ID                                   NAME           CREATED        CONNECTOR{RESET}",
            "2a3b4c5d-6e7f-8a9b-0c1d-2e3f4a5b6c7d novaprotocol   2026-05-01     1 connector",
        ],
    },
    {
        "input": "cloudflared tunnel info novaprotocol",
        "output": [
            f"NAME      : {GREEN}novaprotocol{RESET}",
            "ID        : 2a3b4c5d-6e7f-8a9b-0c1d-2e3f4a5b6c7d",
            "CONNECTOR : 1 active",
            "INGRESS   : https://github.projectnova.download -> http://localhost:7050",
        ],
    },
    {
        "input": "curl -s https://github.projectnova.download/health",
        "output": [f'{GREEN}{{"status":"ok"}}{RESET}'],
    },
    {
        "input": "systemctl status caddy",
        "output": [
            f"{GREEN}\u25cf caddy.service \u2014 Caddy web server{RESET}",
            f"{GREEN}   Active: active (running) since Sun 2026-08-09{RESET}",
        ],
    },
    {
        "input": "exit",
        "output": ["logout", "Connection to ProjectNova.remote closed."],
    },
    {"input": "", "output": [], "custom_prefix": "PS C:\\Users\\khyles> "},
]


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
