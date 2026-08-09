# Design: NovaProtocol Asset SVG Rebuild

**Date:** 2026-08-09

## Overview

Rebuild the animated SVGs served by the NovaProtocol FastAPI asset server.
Replace the current hand-rolled SVG string generation and the code+terminal
"typing" combo with two library-driven SVGs:

- `/name.svg` — green terminal-style name with a typed reveal.
- `/console.svg` — a plain terminal-window animation showing a scripted bash
  session with realistic (simulated) server-management commands and replies.

Use a mature PyPI library (`SVGwrite`) for all SVG construction. Do not
reinvent SVG generation; do not hand-assemble SVG markup.

## Goals / Non-Goals

**Goals**

- Maintainable, library-driven SVG generation.
- Two endpoints: `/name.svg` and `/console.svg`.
- Animations look like a real, colored terminal.
- Dynamic generation, no caching, no on-disk artifact pipeline.

**Non-Goals**

- No pixel-perfect reproduction of the old SVGs.
- No GIF output.
- No backend behavior change beyond removing old typing generation.

## Routes

| Route        | Content                                                        |
|--------------|----------------------------------------------------------------|
| `/name.svg`  | Green terminal-style name animation                            |
| `/console.svg` | Plain terminal window, scripted bash session animation       |

Both serve `image/svg+xml` with `Cache-Control: no-store, max-age=0`.

The old `/typing.svg` and its startup/gitignored `static/assets/typing_*.svg`
generation are removed. The README badge links and the test-page rewrite map
(`apps/test_page.py`) are updated to point at `/console.svg`.

## Technology

- **`SVGwrite`** (PyPI) — declarative, object-oriented SVG construction with
  animation elements (`animate`, `animateTransform`). Single rendering layer.
- Existing FastAPI app, routes, config remain.

## Component: name SVG

- `viewBox`: `980 x 160`, background `#0D1117`.
- Monospace font stack (DejaVu Sans Mono / Menlo / Consolas / monospace).
- Two lines, typed via reveal animation, **non-looping** (hold final state):
  - Line 1: `> Nova` — large (~64px), green (`#50c878`).
  - Line 2: `> Khyles Gibrian Ramos` — smaller (~24px), dimmer green
    (`#2f8f54`-ish / `#3aa75f`).
- A green block cursor `▊` blinks at the end of the active line, then the
  session holds with a static cursor.

## Component: console SVG

- A **plain** terminal window: dark background, thin border, a compact title
  bar showing `nova@ProjectNova: ~ — bash` (text only, no window dots).
- A scripted bash session on one long, non-looping timeline. Each command is
  typed with a blinking cursor, then its simulated output appears.
- Prompt prefix: `nova@ProjectNova:~$`.

**Session script (simulated, realistic for this stack):**

1. `nova@ProjectNova:~$ gerp -i error /var/log/app.log`
   → `bash: gerp: command not found`
   - comic typo, corrected next
2. `nova@ProjectNova:~$ grep -i error /var/log/app.log`
   → a couple of realistic log lines (some colored)
3. `nova@ProjectNova:~$ df -h`
   → filesystem table (filesystem, size, used, avail, use%, mounted on)
4. `nova@ProjectNova:~$ uptime`
   → `  load average: ...` line
5. `nova@ProjectNova:~$ docker ps`
   → container table: `novaprotocol_main`, `novaprotocol_caddy`
6. `nova@ProjectNova:~$ docker logs novaprotocol_main --tail 15`
   → FastAPI/uvicorn access + startup lines
7. `nova@ProjectNova:~$ systemctl status caddy`
   → `● caddy.service — Caddy ... Active: active (running) ...`
8. `nova@ProjectNova:~$ curl -s http://localhost:7051/health`
   → `{"status":"ok"}`
9. `nova@ProjectNova:~$ exit`
   → (session ends, cursor holds) or simply ends after last output

Not every command must be an error-first typo. Typos appear selectively
(grep gets `gerp`; maybe `systemctl status` typed as `systemctl statsu` once),
but most commands type cleanly. Error/typo output is colored red; warnings
yellow; success/paths blue; values green.

Session ends holding the final screen with a static cursor.

## Server behavior

- Both endpoints render SVG **on every request** (pure functions), with
  `Cache-Control: no-store, max-age=0`.
- Remove the startup `lifespan` generation of `typing_*.svg`.
- Delete `scripts/make_svg.py` and `scripts/make_typing.py`.
- Delete gitignored `static/assets/typing_*.svg` artifacts.
- Add `svgwrite` to `requirements.txt`.

## Testing

- Add `svgwrite` to requirements; run app in debug mode.
- Manual verification: fetch `/name.svg` and `/console.svg`, confirm valid SVG
  and rendering.
- Update `apps/test_page.py` rewrite map (`typing.svg` → `console.svg`) and the
  README badge link.
- No automated test suite exists; keep manual verification approach, but ensure
  both endpoints return 200 + `image/svg+xml`.
