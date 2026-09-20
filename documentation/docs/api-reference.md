# API Reference

NovaProtocol is an **HTTP-only** asset server, every route is a `GET` on the monolith `apps/routes.py` `APIRouter`. All routes are public (no auth, no rate limit beyond the tunnel edge).

## Base URL

- Local dev: `http://127.0.0.1:8000`
- Via Caddy: `http://127.0.0.1:7050` (same routes, `/health` handled explicitly)
- Production: `https://github.projectnova.download` (Cloudflare Tunnel → `127.0.0.1:7050` → `novaprotocol_main:8000`)

Caddy does not strip prefixes for the app, it `reverse_proxy novaprotocol_main:8000` with the original path. `/documentation/*` is the only `handle_path` (docs service, see [Docker & Deployment](docker.md)).

## Endpoints

### `GET /`

Liveness summary, also serves as the app's root info.

- **Response:** `200 application/json`

```json
{"service": "NovaProtocol Assets", "status": "ok"}
```

- **Caddy:** public (falls through to `handle { reverse_proxy novaprotocol_main:8000 }`).
- **Use:** quick check that the factory booted.

---

### `GET /health`

Health probe for compose and tunnel checks.

- **Response:** `200 application/json`

```json
{"status": "ok"}
```

- **Caddy:** `handle /health { reverse_proxy novaprotocol_main:8000 }`, explicit public bypass.
- **Compose healthcheck:** `python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"` with `interval: 30s`, `timeout: 5s`, `retries: 3`, `start_period: 10s`.

```bash
curl -s http://127.0.0.1:8000/health
curl -s http://127.0.0.1:7050/health # via Caddy
curl -s https://github.projectnova.download/health # prod via tunnel
```

---

### `GET /public/name.svg`

Name badge, NOVA block art + identity. See [Name Badge](svg-badges/name-svg.md).

- **Response:** `200 image/svg+xml`, `Cache-Control: public, max-age=300`, plus a strong `ETag`
- **Body:** SVG string from `apps/name_svg.py::render_name_svg()` via `utilities/terminal_svg`.
- **Example:**

```bash
curl -s http://127.0.0.1:8000/public/name.svg | head -c 200
# <?xml version="1.0" encoding="utf-8" ?>
# <svg viewBox="0 0 880 226" ...>
```

- **Embed:**

```html
<img src="https://github.projectnova.download/public/name.svg" alt="name" />
```

---

### `GET /public/console.svg`

Console badge, boot + compose + tunnel bring-up narrative. See [Console Badge](svg-badges/console-svg.md).

- **Response:** `200 image/svg+xml`, `Cache-Control: public, max-age=300`, plus a strong `ETag`
- **Body:** SVG from `apps/console_svg.py::render_console_svg(max_line=8)`.
- **Embed:**

```html
<img src="https://github.projectnova.download/public/console.svg" alt="console" />
```

---

### `GET /public/skills.svg`

Skills badge, career panes (summary, stack, cert, projects). See [Skills Badge](svg-badges/skills-svg.md).

- **Response:** `200 image/svg+xml`, `Cache-Control: public, max-age=300`, plus a strong `ETag`
- **Body:** SVG from `apps/skills_svg.py::render_skills_svg()` (`max_line=20`).
- **Embed:**

```html
<img src="https://github.projectnova.download/public/skills.svg" alt="skills" />
```

---

### `GET /name.svg`, `/console.svg`, `/skills.svg` (legacy)

Legacy aliases, `301` to `/public/*.svg` (kept for camo cache, will not be documented as canonical). Prefer `https://github.projectnova.download/public/*.svg`.

- **Response:** `301 Location: /public/*.svg`

### `GET /public`

Index of public assets, HTML listing `/public/name.svg`, `/public/skills.svg`, `/public/console.svg`.

### `GET /test`

Live SVG gallery, self-contained HTML page embedding the three live badges via `<object>` so SMIL animations run even though GitHub's Markdown strips `<object>`.

- **Response:** `200 text/html; charset=utf-8`
- **Body:** HTML from `apps/test_page.py::render_test_page()`:

```html
<!doctype html>
<html lang="en">
<head>…</head>
<body>
<h1>Live profile assets</h1>
<object type="image/svg+xml" data="/public/name.svg"></object>
<object type="image/svg+xml" data="/public/skills.svg"></object>
<object type="image/svg+xml" data="/public/console.svg"></object>
</body>
</html>
```

- **Use:** manual QA, `http://127.0.0.1:8000/test` in dev, `https://github.projectnova.download/test` in prod. Unlike the SVG routes, this page is `text/html` and sets no cache policy of its own.

---

## Headers & Caching

| Route | `Content-Type` | `Cache-Control` |
|-------|----------------|-----------------|
| `/`, `/health` | `application/json` | *(none)*, JSON, not cached by camo |
| `/public/name.svg`, `/public/console.svg`, `/public/skills.svg` | `image/svg+xml` | `public, max-age=300` + `ETag` |
| `/name.svg`, `/console.svg`, `/skills.svg` | `301 → /public/*.svg` | *(redirect)* |
| `/test` | `text/html; charset=utf-8` | *(none)* |
| `/documentation/*` (docs service) | `text/html` / assets | *(docs FastAPI defaults)* |

SVG responses carry a strong `ETag` derived from the rendered bytes, so a cache stores the render and then revalidates it: an `If-None-Match` that matches answers `304 Not Modified` with no body, and a changed render answers `200` with the new bytes. `public, max-age=300` is deliberate, a `private` response is skipped by every shared cache, so `public` is what lets Cloudflare and GitHub's image proxy (camo) store it, and the five-minute window bounds how long a change can go unseen if a cache never revalidates. The SVG is still rendered per request; the `ETag` makes a repeat fetch cheap, it does not cache the render itself.

Measured behaviour worth knowing: camo applies roughly a 60-second lifetime to these URLs regardless of the origin header, so the practical staleness is about a minute, not the full five minutes. The animation cannot go stale in any case, its SMIL timings are relative to the SVG's own start, so a replayed copy plays from the beginning.

## Error Handling

Unknown paths return FastAPI's default `404 application/json`:

```json
{"detail": "Not found"}
```

No custom error pages, the only unknown-route test asserts that an old badge path is gone:

```python
def test_old_typing_route_gone():
 with TestClient(create_app()) as client:
 assert client.get("/typing.svg").status_code == 404
```

## OpenAPI

FastAPI auto-generates `/docs` (Swagger UI) and `/openapi.json` when `DEBUG=True` (`DEPLOYMENT_TYPE=debug`). In `DEPLOYMENT_TYPE=production` the docs are still mounted but not expected to be visited, the public surface is the four badge/gallery routes plus health.

## Relationship to Docs Service

The app's `APIRouter` does **not** include `/documentation/*`, that prefix is intercepted by Caddy (`handle_path /documentation/* → novaprotocol_documentation:8005`). The docs FastAPI serves MkDocs `site/` (see [Docker & Deployment](docker.md) and `documentation/app.py`). A request to `https://github.projectnova.download/documentation/` never reaches `novaprotocol_main:8000`.

## Testing Routes

`tests/test_routes.py`:

```python
def test_health_ok(): ...
def test_name_svg_route(): ... # now 301 → /public/name.svg
def test_console_svg_route(): ...
def test_skills_svg_route(): ...
def test_old_typing_route_gone(): ...
```

Run: `pytest -q` or `pytest tests/test_routes.py -q`.
