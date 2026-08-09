from __future__ import annotations

from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent.parent / "static" / "assets"

W, H = 980, 460
CODE_W = 700
CHAR_H = 22
CODE_FONT = 14
TERM_FONT = 11
MAX_VISIBLE = 18  # number of line-number rows shown, regardless of code length

START_DELAY = 1.0  # seconds the typing animation waits (frozen) before starting

# Colors
BG = "#0D1117"
TITLE_BG = "#22262e"
BORDER = "#30353e"
FG = "#c8d2dc"
GRAY = "#828c9b"
ACCENT = "#50c878"
BLUE = "#6ea0eb"
PINK = "#e678be"
YELLOW = "#e6c85a"
RED_DOT = "#ff5f56"
YELLOW_DOT = "#ffbd2e"
GREEN_DOT = "#27c93f"

# Demo scripts: (filename, [(code_line, is_python), ...], [terminal lines])
DEMOS = [
    (
        "app.py",
        [
            ("from flask import Flask, jsonify, request", True),
            ("from flask_cors import CORS", True),
            ("from datetime import datetime", True),
            ("", True),
            ("app = Flask(__name__)", True),
            ("CORS(app)", True),
            ("", True),
            ("DB = {", True),
            ("    1: {\"name\": \"Portfolio\", \"tech\": \"Flask\"},", True),
            ("    2: {\"name\": \"GateKeeper\", \"tech\": \"Flask\"},", True),
            ("    3: {\"name\": \"WaterBilling\", \"tech\": \"FastAPI\"},", True),
            ("}", True),
            ("", True),
            ('@app.route("/")', True),
            ("def home():", True),
            ("    return jsonify({\"service\": \"nova\", \"status\": \"ok\"})", True),
            ("", True),
            ('@app.route("/api/projects")', True),
            ("def list_projects():", True),
            ("    return jsonify(list(DB.values()))", True),
            ("", True),
            ('@app.route("/api/projects/<int:pid>")', True),
            ("def get_project(pid):", True),
            ("    if pid not in DB:", True),
            ("        return jsonify({\"error\": \"not found\"}), 404", True),
            ("    return jsonify(DB[pid])", True),
            ("", True),
            ('@app.route("/health")', True),
            ("def health():", True),
            ("    return jsonify({\"ok\": True, \"time\": now_iso()})", True),
        ],
        [
            ("$ python app.py", ACCENT),
            (" * Serving Flask app \"app\"", GRAY),
            (" * Running on 127.0.0.1:5000", ACCENT),
            ("127.0.0.1 - \"GET /api/projects\" 200", ACCENT),
            ("✓ API ready — 3 routes registered", YELLOW),
        ],
        "<spin> Serving API requests",
    ),
    (
        "Dockerfile",
        [
            ("# syntax=docker/dockerfile:1", False),
            ("FROM python:3.12-slim AS base", False),
            ("", False),
            ("ENV PYTHONDONTWRITEBYTECODE=1", False),
            ("ENV PYTHONUNBUFFERED=1", False),
            ("", False),
            ("WORKDIR /app", False),
            ("", False),
            ("COPY requirements.txt .", False),
            ("RUN pip install --no-cache-dir -r requirements.txt", False),
            ("", False),
            ("COPY . .", False),
            ("", False),
            ("FROM base AS dev", False),
            ("RUN pip install --no-cache-dir debugpy", False),
            ("CMD [\"granian\", \"--interface\", \"asgi\", \"--reload\", \"wsgi:app\"]", False),
            ("", False),
            ("FROM base AS prod", False),
            ("RUN adduser --disabled-password appuser", False),
            ("USER appuser", False),
            ("", False),
            ("EXPOSE 5000", False),
            ('CMD ["granian", "--interface", "asgi", "--workers", "4", "wsgi:app"]', False),
        ],
        [
            ("$ docker build -t portfolio:prod .", ACCENT),
            ("Step 8/22 : RUN pip install ...", GRAY),
            (" ✓ 24 packages installed", ACCENT),
            ("Step 20/22 : USER appuser", GRAY),
            ("Successfully tagged portfolio:prod", ACCENT),
        ],
        "<spin> Building next container",
    ),
    (
        "Caddyfile",
        [
            ("# Global options", False),
            ("{", False),
            ("    admin off", False),
            ("    email admin@projectnova.download", False),
            ("}", False),
            ("", False),
            ("portfolio.projectnova.download {", False),
            ("    encode gzip zstd", False),
            ("", False),
            ("    handle /health {", False),
            ("        respond \"ok\" 200", False),
            ("    }", False),
            ("", False),
            ("    handle {", False),
            ("        reverse_proxy portfolio_main:7010", False),
            ("    }", False),
            ("", False),
            ("    header /* {", False),
            ("        -Server", False),
            ("        X-Powered-By \"nova\"", False),
            ("    }", False),
            ("}", False),
            ("", False),
            ("api.projectnova.download {", False),
            ("    reverse_proxy api_main:8000", False),
            ("}", False),
        ],
        [
            ("$ caddy run --config Caddyfile", ACCENT),
            ("serving initial configuration", GRAY),
            ("portfolio.projectnova.download 200", ACCENT),
            ("api.projectnova.download 200", ACCENT),
        ],
        "<spin> Listening for requests",
    ),
    (
        "config.yml",
        [
            ("tunnel: abc-def-123", False),
            ("credentials-file: .cloudflared/creds.json", False),
            ("", False),
            ("ingress:", False),
            ("  - hostname: portfolio.projectnova.download", False),
            ("    service: http://localhost:7010", False),
            ("", False),
            ("  - hostname: api.projectnova.download", False),
            ("    service: http://localhost:8000", False),
            ("", False),
            ("  - hostname: meter.projectnova.download", False),
            ("    service: http://localhost:8080", False),
            ("", False),
            ("  - hostname: gate.projectnova.download", False),
            ("    service: gatekeeper:7000", False),
            ("", False),
            ("  - service: http_status:404", False),
        ],
        [
            ("$ cloudflared tunnel run", ACCENT),
            ("Registered tunnel connection", GRAY),
            ("connector established", ACCENT),
            ("4 hostnames mapped to services", ACCENT),
        ],
        "<spin> Opening next tunnel",
    ),
    (
        "gunicorn.conf.py",
        [
            ("import multiprocessing", True),
            ("import os", True),
            ("", True),
            ("bind = \"0.0.0.0:5000\"", True),
            ("workers = multiprocessing.cpu_count() * 2 + 1", True),
            ("threads = 2", True),
            ('worker_class = "gthread"', True),
            ("timeout = 30", True),
            ("graceful_timeout = 30", True),
            ("keepalive = 5", True),
            ("", True),
            ('accesslog = "-"', True),
            ('errorlog = "-"', True),
            ("loglevel = \"info\"", True),
            ("", True),
            ("def post_fork(server, worker):", True),
            ("    server.log.info(\"Worker spawned: %s\", worker.pid)", True),
            ("", True),
            ("def on_exit(server):", True),
            ("    server.log.info(\"Server shutting down\")", True),
        ],
        [
            ("$ gunicorn -c gunicorn.conf.py", ACCENT),
            ("Listening at: http://0.0.0.0:5000", GRAY),
            ("Booting worker with pid: 1234", ACCENT),
            ("Worker spawned: 1234", ACCENT),
        ],
        "<spin> Spawning next worker",
    ),
    (
        "MeterReader.tsx",
        [
            ("import { NfcManager, NfcTech } from \"react-native-nfc-manager\";", True),
            ("import { StyleSheet, Text, View, Pressable } from \"react-native\";", True),
            ("import { useState } from \"react\";", True),
            ("", True),
            ("type Reading = {", True),
            ("    meterId: string;", True),
            ("    usage: number;", True),
            ("    ts: string;", True),
            ("};", True),
            ("", True),
            ("export default function MeterReader() {", True),
            ("    const [reading, setReading] = useState<Reading | null>(null);", True),
            ("", True),
            ("    async function tapMeter(tag: string) {", True),
            ("        try {", True),
            ("            await NfcManager.requestTechnology(NfcTech.Ndef);", True),
            ("            const bytes = await NfcManager.getTag();", True),
            ("            const usage = parseUsage(bytes);", True),
            ("            setReading({ meterId: tag, usage, ts });", True),
            ("        } finally {", True),
            ("            NfcManager.cancelTechnologyRequest();", True),
            ("        }", True),
            ("    }", True),
            ("", True),
            ("    return (", True),
            ("        <View style={styles.wrap}>", True),
            ("            <Pressable onPress={() => tapMeter(\"NTAG215\")}>", True),
            ("                <Text>Tap meter</Text>", True),
            ("            </Pressable>", True),
            ("        </View>", True),
            ("    );", True),
            ("}", True),
        ],
        [
            ("$ npx expo run:android", ACCENT),
            ("▸ Bundled 214ms", GRAY),
            ("Meter NFC tag read: NTAG215", ACCENT),
            ("usage: 12.4 m³ saved", ACCENT),
        ],
        "<spin> Scanning next meter",
    ),
]

# typing timing: constant per-char delay, no per-line delay
PER_CHAR = 0.02       # seconds per keystroke (matches portfolio ~50 chars/sec)
SPIN_TIME = 2.0       # seconds of loading spinner at end
SPIN = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def highlight_python(line: str) -> str:
    """Return svg tspans with syntax coloring."""
    keywords = {"from", "import", "def", "return", "class", "if", "app"}
    tokens = []
    i = 0
    n = len(line)
    while i < n:
        ch = line[i]
        if ch == '"':
            j = line.find('"', i + 1)
            if j == -1:
                j = n
            tokens.append((line[i:j + 1], PINK))
            i = j + 1
        elif ch == "#":
            tokens.append((line[i:], GRAY))
            break
        elif ch.isalpha() or ch == "_":
            j = i
            while j < n and (line[j].isalnum() or line[j] == "_"):
                j += 1
            word = line[i:j]
            color = BLUE if word in keywords else FG
            tokens.append((word, color))
            i = j
        elif ch == "@":
            j = i
            while j < n and not line[j].isspace():
                j += 1
            tokens.append((line[i:j], YELLOW))
            i = j
        else:
            tokens.append((ch, FG))
            i += 1
    return "".join(f'<tspan fill="{color}">{esc(t)}</tspan>' for t, color in tokens)


def build_demo_svg(filename: str, code: list[tuple[str, bool]], term: list[tuple[str, str]], load_msg: str) -> str:
    code_x = 48
    lines_start_y = 44
    cursor_w = 9

    # Variable timing: constant per-char delay, no per-line delay. The whole
    # timeline is offset by START_DELAY so the animation stays frozen for the
    # first second (while the name plays), then types once and freezes.
    char_w = CODE_FONT * 0.6  # approx mono char width at the code font size

    # absolute times (seconds). Offset by START_DELAY.
    t = START_DELAY
    line_abs = []  # (start, end, hold_until) per code line
    for l in code:
        n = len(l[0])  # blank lines = 0 chars = instant
        start = t
        t += n * PER_CHAR
        end = t
        line_abs.append((start, end, end))

    # Extend cursor hold: a non-blank line's cursor stays visible through any
    # blank lines that follow, until the next non-blank line starts.
    for i in reversed(range(len(line_abs))):
        s, e, h = line_abs[i]
        if i + 1 < len(line_abs):
            next_s, _, _ = line_abs[i + 1]
            h = next_s  # hold until next line starts (includes blank line gaps)
        line_abs[i] = (s, e, h)

    out_abs = []  # (start, end) seconds per output line; reveals whole line at end
    for text, _ in term:
        n = len(text)
        start = t
        t += n * PER_CHAR * 0.75  # 0.75x per-char timing
        end = t
        out_abs.append((start, end))

    load_abs = (t, t + SPIN_TIME)  # load message appears at end of output
    spin_start = t
    t += SPIN_TIME
    total = t  # variable total duration in seconds

    # fractions for keyTimes
    def frac(s: float) -> float:
        return min(s / total, 0.999)

    line_windows = []
    for (s, e, h), l in zip(line_abs, code):
        line_windows.append((frac(s), frac(e), frac(h), len(l[0]) * char_w))
    out_windows = [(frac(s), frac(e)) for s, e in out_abs]
    load_window = (frac(load_abs[0]), frac(load_abs[1]))
    spinner_frac = frac(spin_start)

    clips = []
    code_elems = []
    for i, (line, is_py) in enumerate(code):
        y = lines_start_y + i * CHAR_H
        rid = f"clip{i}"
        s, e, h, lw = line_windows[i]
        # clip width ramps 0 -> full text width continuously during [s, e]
        clips.append(
            f'<clipPath id="{rid}">'
            f'<rect x="{code_x}" y="{y - 18}" width="0" height="{CHAR_H}">'
            f'<animate attributeName="width" dur="{total:.2f}s" fill="freeze" '
            f'values="0;0;3000;3000" keyTimes="0;{s:.4f};{min(e, 0.999):.4f};1"/></rect></clipPath>'
        )
        content = highlight_python(line) if is_py else f'<tspan fill="{FG}">{esc(line)}</tspan>'
        # code text only (no inline cursor glyph; cursor is a separate element)
        code_elems.append(
            f'<text x="{code_x}" y="{y}" font-size="{CODE_FONT}" clip-path="url(#{rid})" xml:space="preserve">{content}</text>'
        )

    cursor_elems: list[str] = []

    # Single block cursor: a filled rect that moves down line-by-line and right
    # as text is typed. It lives inside the scroll group so it scrolls with code.
    # x animates from code_x to code_x+line_width over each line's typing window;
    # y jumps to each line's row. Only visible while typing.
    if code:
        x_kt = ["0"]
        x_vals = ["0"]
        y_kt = ["0"]
        y_vals = [str(lines_start_y - 20)]
        for i, (line, _is_py) in enumerate(code):
            s, e, h, lw = line_windows[i]
            if len(line) == 0:
                continue
            x_kt.extend([f"{s:.4f}", f"{min(e, 0.999):.4f}"])
            x_vals.extend(["0", f"{lw:.1f}"])
            y_kt.extend([f"{s:.4f}", f"{min(e, 0.999):.4f}"])
            y_vals.extend([f"{lines_start_y + i * CHAR_H - 20}", f"{lines_start_y + i * CHAR_H - 20}"])
        cursor_elems.append(
            f'<rect x="{code_x}" y="0" width="10" height="{CHAR_H}" fill="{ACCENT}" opacity="0.8">'
            f'<animateTransform attributeName="transform" type="translate" '
            f'dur="{total:.2f}s" fill="freeze" '
            f'values="{";".join(x_vals)}" keyTimes="{";".join(x_kt)}"/>'
            f'<animate attributeName="y" dur="{total:.2f}s" fill="freeze" '
            f'values="{";".join(y_vals)}" keyTimes="{";".join(y_kt)}"/>'
            f'</rect>'
        )

    # terminal output: each line appears as a whole, abruptly (no fade), at the
    # end of its window.
    n_term = len(term)
    out_elems = []
    for i, (text, color) in enumerate(term):
        y = 100 + i * 20
        s, e = out_windows[i]
        out_elems.append(
            f'<text x="{CODE_W + 22}" y="{y}" font-size="{TERM_FONT}" fill="{color}">'
            f'<tspan>{esc(text)}</tspan>'
            f'<animate attributeName="opacity" dur="{total:.2f}s" fill="freeze" '
            f'values="0;0;1;1" keyTimes="0;{min(e, 0.999):.4f};{min(e + 0.001, 0.999):.4f};1"/>'
            f'</text>'
        )

    # load message: appears abruptly as a terminal line at the end of output,
    # then its <spin> character cycles to animate a spinner for 2s.
    load_y = 100 + n_term * 20
    ls, le = load_window
    load_text = load_msg.replace("<spin>", "{}")
    spin_frac = (le - ls) / len(SPIN)  # per-char fraction within the load window
    spinner_elems = []
    for k, ch in enumerate(SPIN):
        msg = load_text.format(ch) if "{}" in load_text else load_msg
        a = round(ls + spin_frac * k, 4)
        b = round(ls + spin_frac * (k + 1), 4)
        spinner_elems.append(
            f'<text x="{CODE_W + 22}" y="{load_y}" font-size="{TERM_FONT}" fill="{ACCENT}">'
            f'<tspan>{esc(msg)}</tspan>'
            f'<animate attributeName="opacity" dur="{total:.2f}s" fill="freeze" '
            f'values="0;0;1;1;0;0" keyTimes="0;{min(a, 0.999):.4f};{min(a + 0.001, 0.999):.4f};{min(b - 0.001, 0.999):.4f};{min(b, 0.999):.4f};1"/></text>'
        )

    out_clips: list[str] = []

    # Scrolling code pane: render line numbers + code in one group, and scroll
    # it up as typing progresses past the viewport. A clip path keeps only the
    # MAX_VISIBLE rows visible.
    n_code = len(code)
    viewport = (
        f'<clipPath id="codeview"><rect x="0" y="{lines_start_y - 20}" '
        f'width="{CODE_W}" height="{MAX_VISIBLE * CHAR_H + 20}"/></clipPath>'
        f'<clipPath id="termview"><rect x="{CODE_W + 14}" y="44" '
        f'width="{W - CODE_W - 26}" height="{H - 56}"/></clipPath>'
    )

    all_lineno = []
    for i in range(n_code):
        y = lines_start_y + i * CHAR_H
        all_lineno.append(
            f'<text x="{code_x - 14}" y="{y}" font-size="{CODE_FONT}" opacity="0.25" fill="{GRAY}" text-anchor="end">{i + 1}</text>'
        )

    max_scroll = max(0, n_code - MAX_VISIBLE)
    scroll_anim = ""
    if max_scroll > 0:
        kt = ["0"]
        vals = ["0,0"]
        last = 0.0
        for i in range(MAX_VISIBLE + 1, n_code + 1):
            # when line i starts typing, scroll so it's visible (one row up)
            s_i = frac(line_abs[i - 1][0])
            if s_i > last:
                kt.append(f"{s_i:.4f}")
                vals.append(f"0,-{(i - MAX_VISIBLE) * CHAR_H}")
                last = s_i
        if last < 0.999:
            kt.append("0.999")
            vals.append(f"0,-{max_scroll * CHAR_H}")
        kt.append("1")
        vals.append(f"0,-{max_scroll * CHAR_H}")
        scroll_anim = (
            f'<animateTransform attributeName="transform" type="translate" '
            f'dur="{total:.2f}s" fill="freeze" '
            f'values="{";".join(vals)}" keyTimes="{";".join(kt)}" calcMode="discrete"/>'
        )

    svg = f'''<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" font-family="DejaVu Sans Mono, Menlo, Consolas, Liberation Mono, Courier New, monospace">
<defs>{''.join(clips)}{viewport}{''.join(out_clips)}
</defs>
<rect width="{W}" height="{H}" fill="{BG}"/>
<line x1="{CODE_W}" y1="0" x2="{CODE_W}" y2="{H}" stroke="{BORDER}" stroke-width="2"/>
<g clip-path="url(#codeview)">
<g>
{scroll_anim}
{''.join(all_lineno)}
{''.join(code_elems)}
{''.join(cursor_elems)}
</g>
</g>
<rect x="{CODE_W + 14}" y="44" width="{W - CODE_W - 26}" height="{H - 56}" rx="6" fill="none" stroke="{BORDER}"/>
<rect x="{CODE_W + 14}" y="44" width="{W - CODE_W - 26}" height="24" rx="6" fill="{TITLE_BG}"/>
<text x="{CODE_W + 24}" y="61" font-size="13" fill="{GRAY}">terminal</text>
<g clip-path="url(#termview)">
{''.join(out_elems)}
{''.join(spinner_elems)}
</g>
</svg>'''
    return svg


def generate() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    total = 0
    for i, (filename, code, term, load_msg) in enumerate(DEMOS):
        svg = build_demo_svg(filename, code, term, load_msg)
        safe = Path(filename).stem.replace(" ", "_").lower()
        out = OUT_DIR / f"typing_{i}_{safe}.svg"
        out.write_text(svg)
        total += out.stat().st_size
        print(f"wrote {out.name} ({out.stat().st_size} bytes)")
    print(f"total: {total} bytes across {len(DEMOS)} demos")
    return total


if __name__ == "__main__":
    generate()
