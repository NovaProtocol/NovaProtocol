# API Reference

NovaProtocol is an **HTTP-only** asset server — every route is a `GET` on the monolith `apps/routes.py` `APIRouter`. All routes are public (no auth, no rate limit beyond the tunnel edge).

## Base URL

- Local dev: `http://127.0.0.1:7051`
- Via Caddy: `http://127.0.0.1:7050` (same routes, `/health` handled explicitly)
- Production: `https://github.projectnova.download` (Cloudflare Tunnel → `127.0.0.1:7050` → `novaprotocol_main:7051`)

Caddy does not strip prefixes for the app — it `reverse_proxy novaprotocol_main:7051` with the original path. `/documentation/*` is the only `handle_path` (docs service, see [Docker & Deployment](docker.md)).

## Endpoints

### `GET /`

Liveness summary — also serves as the app's root info.

- **Response:** `200 application/json`

```json
{"service": "NovaProtocol Assets", "status": "ok"}
```

- **Caddy:** public (falls through to `handle { reverse_proxy novaprotocol_main:7051 }`).
- **Use:** quick check that the factory booted.

---

### `GET /health`

Health probe for compose and tunnel checks.

- **Response:** `200 application/json`

```json
{"status": "ok"}
```

- **Caddy:** `handle /health { reverse_proxy novaprotocol_main:7051 }` — explicit public bypass.
- **Compose healthcheck:** `python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:7051/health')"` with `interval: 30s`, `timeout: 5s`, `retries: 3`, `start_period: 10s`.

```bash
curl -s http://127.0.0.1:7051/health
curl -s http://127.0.0.1:7050/health       # via Caddy
curl -s https://github.projectnova.download/health  # prod via tunnel
```

---

### `GET /name.svg`

Name badge — NOVA block art + identity. See [Name Badge](svg-badges/name-svg.md).

- **Response:** `200 image/svg+xml`, `Cache-Control: no-store, max-age=0`
- **Body:** SVG string from `apps/name_svg.py::render_name_svg()` via `utilities/terminal_svg`.
- **Example:**

```bash
curl -s http://127.0.0.1:7051/name.svg | head -c 200
# <?xml version="1.0" encoding="utf-8" ?>
# <svg viewBox="0 0 880 226" ...>
```

- **Embed:**

```html
<img src="https://github.projectnova.download/name.svg" alt="name" />
```

---

### `GET /console.svg`

Console badge — boot + compose + tunnel bring-up narrative. See [Console Badge](svg-badges/console-svg.md).

- **Response:** `200 image/svg+xml`, `Cache-Control: no-store, max-age=0`
- **Body:** SVG from `apps/console_svg.py::render_console_svg(max_line=8)`.
- **Embed:**

```html
<img src="https://github.projectnova.download/console.svg" alt="console" />
```

---

### `GET /skills.svg`

Skills badge — career panes (summary, stack, cert, projects). See [Skills Badge](svg-badges/skills-svg.md).

- **Response:** `200 image/svg+xml`, `Cache-Control: no-store, max-age=0`
- **Body:** SVG from `apps/skills_svg.py::render_skills_svg()` (`max_line=20`).
- **Embed:**

```html
<img src="https://github.projectnova.download/skills.svg" alt="skills" />
```

---

### `GET /test`

Live SVG gallery — self-contained HTML page embedding the three live badges via `<object>` so SMIL animations run even though GitHub's Markdown strips `<object>`.

- **Response:** `200 text/html; charset=utf-8`
- **Body:** HTML from `apps/test_page.py::render_test_page()`:

```html
<!doctype html>
<html lang="en">
<head>…</head>
<body>
<h1>Live profile assets</h1>
<object type="image/svg+xml" data="/name.svg"></object>
<object type="image/svg+xml" data="/skills.svg"></object>
<object type="image/svg+xml" data="/console.svg"></object>
</body>
</html>
```

- **Use:** manual QA — `http://127.0.0.1:7051/test` in dev, `https://github.projectnova.download/test` in prod. Unlike the SVG routes, this page is `text/html` and does not set `no-store`.

---

## Headers & Caching

| Route | `Content-Type` | `Cache-Control` |
|-------|----------------|-----------------|
| `/`, `/health` | `application/json` | *(none)* — JSON, not cached by camo |
| `/name.svg`, `/console.svg`, `/skills.svg` | `image/svg+xml` | `no-store, max-age=0` |
| `/test` | `text/html; charset=utf-8` | *(none)* |
| `/documentation/*` (docs service) | `text/html` / assets | *(docs FastAPI defaults)* |

The `no-store` on SVGs is deliberate — GitHub's image proxy (camo) would otherwise cache the first fetch and the animation would go stale. The SVG itself is re-rendered per request (no server-side cache).

## Error Handling

Unknown paths return FastAPI's default `404 application/json`:

```json
{"detail": "Not found"}
```

No custom error pages — the only unknown-route test asserts that an old badge path is gone:

```python
def test_old_typing_route_gone():
    with TestClient(create_app()) as client:
        assert client.get("/typing.svg").status_code == 404
```

## OpenAPI

FastAPI auto-generates `/docs` (Swagger UI) and `/openapi.json` when `DEBUG=True` (`DEPLOYMENT_TYPE=debug`). In `DEPLOYMENT_TYPE=production` the docs are still mounted but not expected to be visited — the public surface is the four badge/gallery routes plus health.

## Relationship to Docs Service

The app's `APIRouter` does **not** include `/documentation/*` — that prefix is intercepted by Caddy (`handle_path /documentation/* → novaprotocol_documentation:8005`). The docs FastAPI serves MkDocs `site/` (see [Docker & Deployment](docker.md) and `documentation/app.py`). A request to `https://github.projectnova.download/documentation/` never reaches `novaprotocol_main:7051`.

## Testing Routes

`tests/test_routes.py`:

```python
def test_health_ok(): ...
def test_name_svg_route(): ...
def test_console_svg_route(): ...
def test_skills_svg_route(): ...
def test_old_typing_route_gone(): ...
```

Run: `pytest -q` or `pytest tests/test_routes.py -q`.
