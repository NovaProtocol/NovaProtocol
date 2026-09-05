# Docker & Deployment

## Compose

`compose.yaml` — three services: `app` + `documentation` + `caddy`. Single `default` network + the shared tunnel external network.

```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: novaprotocol_main
    restart: unless-stopped
    environment:
      DEPLOYMENT_TYPE: ${DEPLOYMENT_TYPE:?DEPLOYMENT_TYPE is required}
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health')"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s
    networks:
      - default

  documentation:
    build:
      context: .
      dockerfile: documentation/Dockerfile
    container_name: novaprotocol_documentation
    restart: unless-stopped
    expose:
      - "8005"
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8005/health')"]
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 10s
    networks:
      - default

  caddy:
    build:
      context: ./caddy
      dockerfile: Dockerfile
    container_name: novaprotocol_caddy
    restart: unless-stopped
    ports:
      - "127.0.0.1:7050:7050"
    networks:
      - default
      - gatekeeper_dynamic
      - cloudflared-tunnel

networks:
  default:
  gatekeeper_dynamic:
    external: true
    name: gatekeeper_dynamic
  cloudflared-tunnel:
    external: true
    name: cloudflared-tunnel_default
```

### Naming

| Compose service | `container_name` | What |
|----------------|------------------|------|
| `app` | `novaprotocol_main` | FastAPI app on `8000` |
| `documentation` | `novaprotocol_documentation` | MkDocs FastAPI on `8005` |
| `caddy` | `novaprotocol_caddy` | Caddy on `7050` |

Caddy proxies to `container_name` (`novaprotocol_main:8000`, `novaprotocol_documentation:8005`), **not** the generic service name `app` — avoids the shared-network DNS gotcha where every `app` alias on `cloudflared-tunnel_default` / `gatekeeper_dynamic` would resolve together (see `reference/docker/compose.md`).

### Environment

Only `DEPLOYMENT_TYPE` (`debug`/`production`), `${VAR:?}` so compose fails fast with a clear message if it is missing:

```bash
export DEPLOYMENT_TYPE=production
docker compose up -d --build
```

No `.env` file, no `env_file:`, no secrets — the monolith has no DB or token (see `.env.example`).

### Healthchecks

- Both app and docs use the Python stdlib `urllib.request` probe — no `curl`/`wget` in the image.
- `start_period: 10s` lets granian bind before the first probe.
- Caddy's `/health` is not healthchecked as a container — it is a forward to the app; tunnel checks hit it directly.

Verify:

```bash
docker inspect novaprotocol_main --format '{{.State.Health.Status}}'           # healthy
docker inspect novaprotocol_documentation --format '{{.State.Health.Status}}'  # healthy
curl -s http://127.0.0.1:8000/health   # direct app
curl -s http://127.0.0.1:8005/health   # direct docs (from sibling or localhost if published)
curl -s http://127.0.0.1:7050/health   # via Caddy
curl -s http://127.0.0.1:7050/documentation/ | head  # docs via Caddy (public)
```

---

## Dockerfiles

### App (`Dockerfile`) — `python:3.14-slim`, `appuser` uid `10001`

```dockerfile
FROM python:3.14-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends fonts-dejavu-core && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python3 -m compileall -q /app 2>/dev/null || true

RUN useradd --create-home --uid 10001 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["granian", "--interface", "asgi", "--host", "0.0.0.0", "--port", "8000", "--workers", "1", "wsgi:app"]
```

- `fonts-dejavu-core` ensures `DejaVu Sans Mono` metrics for badge layout.
- `requirements.txt` is copied and pip-installed **before** `COPY . .` so Docker caches the pip layer.
- `python -m compileall` catches syntax errors at build time.
- Non-root `USER appuser` (uid `10001`) — `docker run --rm novaprotocol_main whoami` → `appuser`.
- `EXPOSE 8000` matches compose/Caddy; `CMD` is exec-form granian ASGI with the `wsgi:app` target.

### Documentation (`documentation/Dockerfile`) — same shape, `mkdocs build`

```dockerfile
FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY documentation/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY documentation/ .

RUN mkdocs build

RUN useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app

EXPOSE 8005

USER appuser

CMD ["granian", "--interface", "asgi", "--host", "0.0.0.0", "--port", "8005", "--workers", "1", "app:app"]
```

- `mkdocs build` runs at image-build time — `site/` is baked in; the container just serves it.
- No fonts needed — docs are HTML, not SVG rendering.
- Same `EXPOSE`, non-root, and granian ASGI pattern as the app.

### Caddy (`caddy/Dockerfile`)

```dockerfile
FROM caddy:2-alpine

COPY Caddyfile /etc/caddy/Caddyfile
```

---

## Caddy

`caddy/Caddyfile` — single port `:7050`, loopback-only via `127.0.0.1:7050:7050` tunnel reachability, **public** (no `forward_auth`).

```caddy
:7050 {
    handle /health {
        reverse_proxy novaprotocol_main:8000
    }

    handle_path /documentation/* {
        reverse_proxy novaprotocol_documentation:8005
    }

    handle {
        reverse_proxy novaprotocol_main:8000
    }
}
```

### Routing

| Path | Caddy directive | Target | Auth |
|------|-----------------|--------|------|
| `/health` | `handle /health` | `novaprotocol_main:8000` | public — tunnel + compose probe |
| `/documentation/*` | `handle_path /documentation/*` | `novaprotocol_documentation:8005` | **public** — prefix-stripped |
| all else (`/`, `/name.svg`, `/console.svg`, `/skills.svg`, `/test`) | `handle` catch-all | `novaprotocol_main:8000` | **public** |

`handle_path` strips the prefix before proxying — the docs app sees `/` for `GET /documentation/` and `/getting-started/` for `GET /documentation/getting-started/`.

!!! note "Intentionally no gatekeeper"
    Unlike Buddys/Portfolio/SolveSpace/WBS, NovaProtocol's Caddyfile has **no** `forward_auth gatekeeper:7000 { uri /api/authz/forward-auth }` and `compose.yaml` does **not** join `gatekeeper_default`. The assets are GitHub profile embeds fetched by camo without cookies — gating would `302` to login and the image would break. Documentation follows the same rule — `/documentation/*` is public. This is the declared exception to `reference/gatekeeper/*` and `reference/docker/caddy.md`.

### Verify Caddy

```bash
docker exec novaprotocol_caddy getent hosts novaprotocol_main
docker exec novaprotocol_caddy getent hosts novaprotocol_documentation
docker compose config | grep -A2 ports
curl -s http://127.0.0.1:7050/health | jq .
curl -s http://127.0.0.1:7050/documentation/ | grep -i "NovaProtocol"
```

---

## Networks

- `default` — bridge, intra-project traffic (Caddy ↔ app, Caddy ↔ docs).
- `cloudflared-tunnel` — external `cloudflared-tunnel_default`, ingress via `cloudflared tunnel` → `http://localhost:7050`.
- No `gatekeeper_default` — see the note above.

TLS is terminated at the tunnel edge (Cloudflare) — Caddy is plain HTTP on `:7050`.

---

## Deployment Model

- **Remote** (`ssh agent-access`, `scripts/docker.sh` wrapper) — local `docker ps` shows dev containers like `dockhand`, not production `novaprotocol_main`. Never `docker compose` against the remote without owner approval.
- The deployed `compose.yaml` lives on the Dokhand host under `/app/data/stacks/…` — not necessarily the repo copy.
- Owner deploys — agents fix code locally and commit; the owner copies `compose.yaml`/`Caddyfile` into Dokhand and recreates.
- No volumes — the app is stateless (no DB, no uploads); docs `site/` is baked into the image.
- Restart policy: `restart: unless-stopped` on every service.

---

## Port Allocation

House rule: ports allotted in groups of **10**. NovaProtocol owns the `7050`s:

| Port | Use |
|------|-----|
| `7050` | Caddy `http` — `127.0.0.1:7050:7050` (via `cloudflared tunnel` → `github.projectnova.download`) |
| `8000` | App granian ASGI — `novaprotocol_main:8000` (`uvicorn` on `8000` in dev via `run.py`) |
| `8005` | Documentation granian ASGI — `novaprotocol_documentation:8005` (`expose:` only, via Caddy `/documentation/*`) |

Verify: `docker compose ps` must show `127.0.0.1:7050->7050/tcp`, not `0.0.0.0`.

---

## Local vs Prod Parity

| Path | Local `run.py` | Prod `granian` |
|------|----------------|----------------|
| Factory | `uvicorn "apps:create_app" factory=True --reload` | `granian --interface asgi --host 0.0.0.0 --port 8000 --workers 1 wsgi:app` |
| Ports | `8000` app, `8005` docs (if run), no Caddy | `7050` Caddy + `8000` app + `8005` docs |
| Reload | in `debug` | never |
| User | your shell user | `appuser` uid `10001` |
