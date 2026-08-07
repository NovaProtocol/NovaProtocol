from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 980, 460
CODE_W = 640          # left pane, wider
TERM_W = W - CODE_W   # right pane

BG = (18, 20, 24)
TITLE_BG = (34, 38, 46)
BORDER = (48, 53, 62)
FG = (200, 210, 220)
GRAY = (130, 140, 155)
ACCENT = (80, 200, 120)
BLUE = (110, 160, 235)
PINK = (230, 120, 190)
YELLOW = (230, 200, 90)
GREEN = (80, 200, 120)
RED_DOT = (255, 95, 86)
YELLOW_DOT = (255, 189, 46)
GREEN_DOT = (39, 201, 63)

FONT_MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONT_SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def _load_font(size: int, mono: bool = True) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [FONT_MONO if mono else FONT_SANS]
    if mono:
        candidates += [
            "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationMono.ttf",
        ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


FONT_CODE = _load_font(17, mono=True)
FONT_TITLE = _load_font(14, mono=False)
FONT_TERM = _load_font(15, mono=True)

CHAR_W = 11
CHAR_H = 22
MAX_VISIBLE = 14          # code lines shown
MAX_COLS = (CODE_W - 14 - 34) // CHAR_W   # wrap width for the code pane
PAIRS = {"(": ")", "[": "]", "{": "}"}
CLOSE = {")", "]", "}"}

# Demo scripts: each is a list of ops.
#  ("type", "text", speed_ms_per_char)
#  ("newline",)
#  ("wait", ms)
#  ("file", "app.py")
#  ("out", [(text, color), ...])
DEMOS = [
    (
        "app.py",
        [
            ("type", "from flask import Flask, jsonify", 24),
            ("newline",),
            ("type", "from flask_cors import CORS", 24),
            ("newline",),
            ("wait", 120),
            ("newline",),
            ("type", "app = Flask(__name__)", 26),
            ("newline",),
            ("type", "CORS(app)", 26),
            ("newline",),
            ("wait", 90),
            ("newline",),
            ("type", "@app.route(\"/api/projects\")", 24),
            ("newline",),
            ("type", "def list_projects():", 26),
            ("newline",),
            ("type", "    projects = [", 22),
            ("newline",),
            ("type", "        {\"id\": 1, \"name\": \"Portfolio\", \"tech\": \"Flask\"},", 12),
            ("newline",),
            ("type", "        {\"id\": 2, \"name\": \"GateKeeper\", \"tech\": \"Flask\"},", 12),
            ("newline",),
            ("type", "        {\"id\": 3, \"name\": \"WaterBilling\", \"tech\": \"Flask\"},", 12),
            ("newline",),
            ("type", "    ]", 26),
            ("newline",),
            ("type", "    return jsonify(projects)", 24),
            ("newline",),
            ("wait", 200),
            ("newline",),
            ("type", "@app.route(\"/api/projects/<int:id>\")", 22),
            ("newline",),
            ("type", "def get_project(id):", 26),
            ("newline",),
            ("type", "    return jsonify({\"id\": id, \"status\": \"active\"})", 18),
            ("newline",),
            ("wait", 260),
            ("newline",),
            ("type", "if __name__ == \"__main__\":", 24),
            ("newline",),
            ("type", "    app.run(host=\"0.0.0.0\", port=5000)", 20),
            ("newline",),
            ("wait", 400),
            ("out", [
                ("$ python app.py", ACCENT),
                ("", GRAY),
                (" * Serving Flask app \"app\"", GRAY),
                (" * Running on http://0.0.0.0:5000", GREEN),
                ("", GRAY),
                ("✓ API ready — 3 routes registered", YELLOW),
            ]),
        ],
    ),
    (
        "Dockerfile",
        [
            ("type", "FROM python:3.12-slim", 26),
            ("newline",),
            ("type", "WORKDIR /app", 26),
            ("newline",),
            ("wait", 120),
            ("newline",),
            ("type", "COPY requirements.txt .", 22),
            ("newline",),
            ("type", "RUN pip install --no-cache-dir -r requirements.txt", 14),
            ("newline",),
            ("type", "COPY . .", 26),
            ("newline",),
            ("wait", 140),
            ("newline",),
            ("type", "EXPOSE 5000", 26),
            ("newline",),
            ("wait", 80),
            ("newline",),
            ("type", "ENV DEPLOYMENT_TYPE=PRODUCTION", 22),
            ("newline",),
            ("type", "ENV PYTHONUNBUFFERED=1", 26),
            ("newline",),
            ("wait", 120),
            ("newline",),
            ("type", "CMD [\"gunicorn\", \"--bind\", \"0.0.0.0:5000\",", 20),
            ("newline",),
            ("type", "          \"--workers\", \"4\", \"wsgi:app\"]", 18),
            ("newline",),
            ("wait", 400),
            ("out", [
                ("$ docker build -t portfolio:latest .", ACCENT),
                ("", GRAY),
                ("Step 5/9 : RUN pip install ...", GRAY),
                (" ✓ 24 packages installed", GREEN),
                ("Successfully built a1b2c3d4", GREEN),
                ("Successfully tagged portfolio:latest", GREEN),
            ]),
        ],
    ),
    (
        "Caddyfile",
        [
            ("type", "portfolio.projectnova.download {", 24),
            ("newline",),
            ("type", "    reverse_proxy portfolio_main:7010", 18),
            ("newline",),
            ("wait", 140),
            ("newline",),
            ("type", "    header /* {", 24),
            ("newline",),
            ("type", "        -Server", 26),
            ("newline",),
            ("type", "    }", 26),
            ("newline",),
            ("type", "}", 26),
            ("newline",),
            ("wait", 260),
            ("out", [
                ("$ caddy run", ACCENT),
                ("", GRAY),
                ("serving initial configuration", GRAY),
                ("portfolio.projectnova.download 200", GREEN),
            ]),
        ],
    ),
    (
        "config.yml",
        [
            ("type", "tunnel: abc-def-123", 24),
            ("newline",),
            ("type", "credentials-file: .cloudflared/creds.json", 18),
            ("newline",),
            ("wait", 120),
            ("newline",),
            ("type", "ingress:", 26),
            ("newline",),
            ("type", "  - hostname: portfolio.projectnova.download", 14),
            ("newline",),
            ("type", "    service: http://localhost:7010", 18),
            ("newline",),
            ("wait", 120),
            ("newline",),
            ("type", "  - service: http_status:404", 22),
            ("newline",),
            ("wait", 260),
            ("out", [
                ("$ cloudflared tunnel run", ACCENT),
                ("", GRAY),
                ("Registered tunnel connection", GRAY),
                ("connector established", GREEN),
            ]),
        ],
    ),
    (
        "gunicorn.conf.py",
        [
            ("type", "workers = 4", 26),
            ("newline",),
            ("type", "threads = 2", 26),
            ("newline",),
            ("type", "bind = \"0.0.0.0:5000\"", 24),
            ("newline",),
            ("type", "worker_class = \"gthread\"", 24),
            ("newline",),
            ("wait", 140),
            ("newline",),
            ("type", "accesslog = \"-\"", 26),
            ("newline",),
            ("type", "graceful_timeout = 30", 24),
            ("newline",),
            ("wait", 300),
            ("out", [
                ("$ gunicorn wsgi:app", ACCENT),
                ("", GRAY),
                ("Listening at: http://0.0.0.0:5000", GRAY),
                ("Booting worker with pid: 1234", GREEN),
            ]),
        ],
    ),
    (
        "MeterReader.tsx",
        [
            ("type", "import { NfcManager } from \"react-native-nfc-manager\";", 18),
            ("newline",),
            ("wait", 120),
            ("newline",),
            ("type", "async function tapMeter(tag: string) {", 20),
            ("newline",),
            ("type", "    const reading = await NfcManager.read();", 16),
            ("newline",),
            ("wait", 120),
            ("newline",),
            ("type", "    await queueReading(tag, reading);", 18),
            ("newline",),
            ("type", "}", 26),
            ("newline",),
            ("wait", 300),
            ("out", [
                ("$ npx expo run:android", ACCENT),
                ("", GRAY),
                ("▸ Bundled 214ms", GRAY),
                ("Meter NFC tag read: NTAG215", GREEN),
            ]),
        ],
    ),
]


class Terminal:
    """Simulates the portfolio typing engine's editor state."""

    def __init__(self) -> None:
        self.lines: list[str] = [""]
        self.row = 0          # cursor row (in lines)
        self.col = 0          # cursor col (in chars)
        self.cursor_on = True

    def type_char(self, ch: str) -> None:
        line = self.lines[self.row]
        if ch in CLOSE and self.col < len(line) and line[self.col] == ch:
            self.col += 1
            return
        if ch in PAIRS:
            self.lines[self.row] = line[:self.col] + ch + PAIRS[ch] + line[self.col:]
            self.col += 1
        else:
            self.lines[self.row] = line[:self.col] + ch + line[self.col:]
            self.col += 1
        # wrap: if the cursor passed the column width, split the line
        if self.col > MAX_COLS:
            self._wrap_line()

    def _wrap_line(self) -> None:
        line = self.lines[self.row]
        keep = line[:MAX_COLS]
        rest = line[MAX_COLS:]
        self.lines[self.row] = keep
        # find logical column offset for the rest
        self.lines.insert(self.row + 1, rest)
        self.row += 1
        self.col -= MAX_COLS

    def newline(self) -> None:
        line = self.lines[self.row]
        after = line[self.col:]
        self.lines[self.row] = line[:self.col]
        self.lines.insert(self.row + 1, after)
        self.row += 1
        self.col = 0

    def visible_lines(self):
        """Return (start_index, lines) of the last MAX_VISIBLE lines."""
        start = max(0, len(self.lines) - MAX_VISIBLE)
        return start, self.lines[start:]


def highlight(line: str) -> list[tuple[str, tuple]]:
    """Return list of (text, color) tokens for syntax highlighting."""
    tokens: list[tuple[str, tuple]] = []
    keywords = {"from", "import", "def", "return", "class", "if", "app"}
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
            if word in keywords:
                tokens.append((word, BLUE))
            else:
                tokens.append((word, FG))
            i = j
        else:
            tokens.append((ch, FG))
            i += 1
    return tokens


def _physical_lines(lines: list[str]) -> list[tuple[str, bool]]:
    """Flatten logical lines into physical rows with a 'show number' flag."""
    out: list[tuple[str, bool]] = []
    for line in lines:
        if len(line) <= MAX_COLS:
            out.append((line, True))
        else:
            out.append((line[:MAX_COLS], True))
            rest = line[MAX_COLS:]
            while rest:
                out.append((rest[:MAX_COLS], False))
                rest = rest[MAX_COLS:]
    return out


SPINNER = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"


def render_frame(term: Terminal, filename: str, out_lines: list[tuple[str, tuple]],
                 phase: str, out_prog: float, spinner: str = "") -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)

    # Title bar
    d.rectangle([0, 0, W, 36], fill=TITLE_BG)
    for i, col in enumerate((RED_DOT, YELLOW_DOT, GREEN_DOT)):
        d.ellipse([16 + i * 18, 12, 16 + i * 18 + 9, 21], fill=col)
    d.text((W // 2 - 70, 9), f"{filename} — nova", font=FONT_TITLE, fill=GRAY)

    # Divider
    d.rectangle([CODE_W - 1, 36, CODE_W + 1, H], fill=BORDER)

    # ---- Code pane ----
    code_x = 14
    phys = _physical_lines(term.lines)
    start = max(0, len(phys) - MAX_VISIBLE)
    shown = phys[start:]
    lineno_w = 34
    y = 50
    # build logical-line start offsets so we can place the cursor
    line_starts: dict[int, int] = {}
    logical_index = 0
    for idx, (_, show_num) in enumerate(phys):
        if show_num:
            line_starts[logical_index] = idx
            logical_index += 1

    for rel, (text, show_num) in enumerate(shown):
        abs_idx = start + rel
        if show_num:
            # find which logical line this physical row starts
            num = 1
            for k, v in line_starts.items():
                if v == abs_idx:
                    num = k + 1
                    break
            d.text((6, y), str(num), font=FONT_CODE, fill=GRAY)
        x = code_x + lineno_w
        for token_text, color in highlight(text):
            d.text((x, y), token_text, font=FONT_CODE, fill=color)
            x += d.textlength(token_text, font=FONT_CODE)
        y += CHAR_H

    # draw block cursor at the logical cursor position
    if phase == "typing" and term.cursor_on:
        cur_logical = term.row
        phys_idx = line_starts.get(cur_logical, 0)
        if phys_idx >= start and phys_idx < start + len(shown):
            rel = phys_idx - start
            cy = 50 + rel * CHAR_H
            xx = code_x + lineno_w + (term.col % MAX_COLS) * CHAR_W
            d.rectangle([xx, cy, xx + 2, cy + CHAR_H - 2], fill=ACCENT)

    # ---- Terminal pane ----
    d.rectangle([CODE_W + 14, 44, W - 12, H - 12], outline=BORDER, width=1)
    d.rectangle([CODE_W + 14, 44, W - 12, 68], fill=TITLE_BG)
    d.text((CODE_W + 24, 50), "terminal", font=FONT_TITLE, fill=GRAY)

    shown_out = int(len(out_lines) * out_prog)
    ty = 80
    for i in range(shown_out):
        text, color = out_lines[i]
        if text == "":
            ty += 20
            continue
        d.text((CODE_W + 22, ty), text, font=FONT_TERM, fill=color)
        ty += 20

    # loading spinner after output completes
    if phase == "loading" and spinner:
        d.text((CODE_W + 22, ty + 2), f"{spinner} loading next demo…", font=FONT_TERM, fill=ACCENT)

    return img


def simulate_demo(demo, skip: int = 3) -> list[Image.Image]:
    filename, ops = demo
    frames: list[Image.Image] = []
    term = Terminal()
    out_lines: list[tuple[str, tuple]] = []
    cursor_blink = 0
    typed_since_frame = 0

    def emit(phase: str, out_prog: float, spinner: str = "") -> None:
        term.cursor_on = (cursor_blink // 3) % 2 == 0
        frames.append(render_frame(term, filename, out_lines, phase, out_prog, spinner))

    for op in ops:
        kind = op[0]
        if kind == "file":
            filename = op[1]
        elif kind == "type":
            text, _speed = op[1], op[2]
            for ch in text:
                term.type_char(ch)
                cursor_blink += 1
                typed_since_frame += 1
                if typed_since_frame >= skip:
                    emit("typing", 0)
                    typed_since_frame = 0
        elif kind == "newline":
            term.newline()
            emit("idle", 0)
        elif kind == "wait":
            term.cursor_on = False
            for _ in range(int(op[1]) // 80):
                frames.append(render_frame(term, filename, out_lines, "idle", 0))
        elif kind == "out":
            out_lines = op[1]
            total = len(out_lines)
            for i in range(1, total + 1):
                frames.append(render_frame(term, filename, out_lines, "output", i / total))
            # brief hold on the result, then a ~2s loading spinner before restart
            for _ in range(10):
                frames.append(render_frame(term, filename, out_lines, "done", 1.0))
            for _ in range(5):  # 5 spinner cycles * 10 frames * 40ms = 2s
                for i, ch in enumerate(SPINNER):
                    frames.append(render_frame(term, filename, out_lines, "loading", 1.0, ch))

    return frames


def generate() -> int:
    import gc

    assets = Path(__file__).resolve().parent.parent / "static" / "assets"
    assets.mkdir(parents=True, exist_ok=True)

    total_bytes = 0
    for di, demo in enumerate(DEMOS):
        filename = demo[0]
        frames = simulate_demo(demo, skip=3)
        frames = [f.resize((W, H), Image.LANCZOS) for f in frames]

        safe = Path(filename).stem.replace(" ", "_").lower()
        out = assets / f"typing_{di}_{safe}.gif"
        frames[0].save(
            out,
            save_all=True,
            append_images=frames[1:],
            duration=40,
            loop=0,
            optimize=True,
            colors=64,
        )
        n = len(frames)
        total_bytes += out.stat().st_size
        print(f"wrote {out.name} ({out.stat().st_size} bytes, {n} frames)")
        del frames
        gc.collect()

    print(f"total: {total_bytes} bytes across {len(DEMOS)} demos")
    return total_bytes


def main() -> None:
    generate()


if __name__ == "__main__":
    main()
