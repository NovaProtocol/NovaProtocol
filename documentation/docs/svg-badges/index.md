# SVG Badges: Overview

NovaProtocol serves **three** public SVG badges, each is a scripted `utilities/terminal_svg` session. The profile `README.md` embeds them:

```markdown
![name](https://github.projectnova.download/name.svg)
![skills](https://github.projectnova.download/skills.svg)
![console](https://github.projectnova.download/console.svg)
```

All three are generated the same way: a `COMMANDS: list[dict]` session script + a `TerminalSVG` view that renders it to an SVG string, served as `image/svg+xml` from a short-lived `public` cache that revalidates on an `ETag`.

## The Three Badges

| Badge | Route | `max_line` | Size | What It Shows |
|-------|-------|------------|------|---------------|
| **Name** | `GET /name.svg` | `8` | `880×~166` | `PS > ssh nova…` → `nova@ProjectNova pwd` → `./introduce_yourself.sh` → green NOVA block art + name/link |
| **Console** | `GET /console.svg` | `8` | `880×~166` | Full boot: `whoami`, `hostname`, `uptime`, `free -h`, `df -h`, `ss -tlnp`, `systemctl`, `docker compose`, `curl /health`, `cloudflared` → `exit` |
| **Skills** | `GET /skills.svg` | `20` | `880×~466` | Career panes via `./get_*.sh`, summary, tech stack, cert, projects, each full-screen (20 lines) × 10s |

Each badge has its own page:

- [Name Badge](name-svg.md), `apps/name_svg.py`
- [Console Badge](console-svg.md), `apps/console_svg.py`
- [Skills Badge](skills-svg.md), `apps/skills_svg.py`

## Serving

```python
# apps/routes.py

_SVG_CACHE = {"Cache-Control": "public, max-age=300"}

def _etag(body: bytes) -> str:
    return '"' + hashlib.sha256(body).hexdigest()[:32] + '"'

def _svg_response(body: bytes, request: Request) -> Response:
    tag = _etag(body)
    if request.headers.get("if-none-match") == tag:
        return Response(status_code=304, headers={**_SVG_CACHE, "ETag": tag})
    return Response(
        content=body,
        media_type="image/svg+xml",
        headers={**_SVG_CACHE, "ETag": tag},
    )

@router.get("/public/name.svg")
async def public_name_route(request: Request):
 return _svg_response(name_svg.render_name_svg().encode("utf-8"), request)
```

`/public/console.svg`, `/public/skills.svg` and `/public/project/{slug}.svg` answer through the
same helper; the legacy `/name.svg` aliases `301` to the `/public/` path.

- `Content-Type: image/svg+xml`, GitHub camo and browsers render as images.
- `Cache-Control: public, max-age=300`, a cache may store the render for five minutes. `public`
  is what lets a shared cache (Cloudflare, camo) store it at all: a `private` response is
  skipped by every shared cache.
- `ETag`, a strong validator over the rendered bytes. A cache that holds a copy sends
  `If-None-Match`; matching bytes answer `304 Not Modified` with no body, changed bytes answer
  `200` with the new render. That is why a cached badge still updates on the next revalidation
  instead of going stale for the full window.
- All three routes are **public**: no `GateKeeper` login, no cookie.

## Live Preview

`GET /test` (`apps/test_page.py`) renders a self-contained gallery that embeds the three live SVGs via `<object>` so SMIL actually runs:

```python
# apps/test_page.py: _render_svg_gallery() builds:
# <object type="image/svg+xml" data="/name.svg">
# <object type="image/svg+xml" data="/skills.svg">
# <object type="image/svg+xml" data="/console.svg">
```

That page is also public and useful for manual QA before pushing a badge tweak.

## Timing Defaults

All three badges share the prompt and base typing feel; only `max_line` and `delay_per_char_input` vary:

```python
view = TerminalSVG(max_line=8) # name & console, compact
view.command_prefix = f"{GREEN}nova@ProjectNova:{BLUE}~{RESET}$ "
view.delay_per_char_input = 0.03 # name, 30ms per char
view.delay_per_char_output = 0.0 # output bursts (1ms per char minimum)

view = TerminalSVG(max_line=20) # skills, tall
view.command_prefix = f"{GREEN}nova@ProjectNova:{BLUE}~{RESET}$ "
view.delay_per_char_input = 0.05 # slightly slower typing for readability
```

Per-entry overrides (`custom_prefix`, `custom_start_delay`, `custom_end_delay`) drive the PowerShell-style `PS ...>` → `password:` → `nova@…$` transition that opens every badge.

## Editing a Badge

1. Edit the `COMMANDS` list in `apps/name_svg.py` / `apps/console_svg.py` / `apps/skills_svg.py`.
2. Colors are inline ANSI (`\x1b[32m`, `\x1b[34m`, …), keep them inside the `input`/`output` strings.
3. Pad `output` to exactly `max_line` rows if you want a “full screen” look (skills pads to 20 with `""` blanks).
4. Restart the dev server (or `docker compose up -d --build app`) and hit `http://127.0.0.1:8000/<name>.svg` or `/test`.
5. Add assertions in `tests/test_*_svg.py` if the badge's observable surface changes (see each badge page).

## Performance

Each SVG is a few hundred KB of `<tspan>` + `<animate>`, no images, no fonts beyond the viewer's monospace fallback, no JS. Rendering is `O(total_chars + rows * scroll_times)` and happens per-request; there is no on-disk cache, the timeline is built fresh each `render_*_svg()` call. For the current session lengths (name ~8 entries, console ~20, skills ~5) the wall-clock cost is negligible (<10ms).

The `ETag` makes a repeat fetch cheap for a cache that revalidates, but it does not make the render itself cheap: the bytes are still produced per request on a cache miss or a revalidation that finds a change. Wrapping `render_*_svg()` with an `lru_cache(maxsize=1)` or pre-rendering at startup would remove that work, and the `ETag` would then be stable rather than recomputed, so it is a safe follow-up if the render cost ever matters.
