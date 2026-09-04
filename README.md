# NovaProtocol

Public FastAPI asset server that renders animated terminal SVGs for the [NovaProtocol GitHub profile](https://github.com/NovaProtocol) — `name.svg`, `console.svg`, `skills.svg` — behind Caddy on `:7050`.

**Stack:** Python 3.14 · FastAPI + Granian · svgwrite · Jinja2 · Caddy 2 (Alpine) · MkDocs Material
**Docs:** MkDocs site at `documentation/`

<div align="center">

![name](https://github.projectnova.download/name.svg)

</div>

<div align="center">

![skills](https://github.projectnova.download/skills.svg)

</div>

<div align="center">

![console](https://github.projectnova.download/console.svg)

</div>

## How it works

```
Request → Caddy :7050 → novaprotocol_main:8000 → FastAPI apps/routes.py
                           ├─ /name.svg, /console.svg, /skills.svg → svgwrite → image/svg+xml
                           ├─ /public/*.svg (alias) → same handlers, for https://github.projectnova.download/public/*
                           └─ /test → HTML gallery, /health → ok
```

All routes are intentionally **public** (no `forward_auth` — `reference/gatekeeper/caddy-setup.md` § When NOT to gate — GitHub camo has no cookie jar).

## Quick Start

```bash
git clone https://github.com/NovaProtocol/NovaProtocol.git
cd NovaProtocol
export DEPLOYMENT_TYPE=production
docker compose up -d --build
```

## Port Overview

| Service | URL |
|---------|-----|
| App | `http://127.0.0.1:7050` via Caddy (internal `novaprotocol_main:8000`) |
| Caddy | `:7050` (`127.0.0.1:7050:7050` loopback-only, tunnel → `127.0.0.1:7050`) |
| Docs | `http://127.0.0.1:7050/documentation/` → `novaprotocol_documentation:8005` |

## Environment

| Variable | Required | Description |
|----------|----------|-------------|
| `DEPLOYMENT_TYPE` | yes | `debug` or `production` (`${DEPLOYMENT_TYPE:?}` in compose) |

No `.env` file is committed. `SECRET_KEY` is not used — this service has no auth.

## Routes

| Route | Purpose |
|-------|---------|
| `GET /`, `GET /health` | Liveness |
| `GET /name.svg`, `/console.svg`, `/skills.svg` | Badges (`image/svg+xml`, `no-store`) |
| `GET /public/name.svg`, `/public/console.svg`, `/public/skills.svg` | Same as above under `public/*` (use `https://github.projectnova.download/public/*.svg` for embeds — single rule to publicise) |
| `GET /public`, `GET /test` | Index / gallery |
| `GET /documentation/*` | MkDocs |

## Auth

Intentionally public — no GateKeeper. `caddy/Caddyfile` has no `forward_auth gatekeeper:7000` (`reference/docker/caddy.md`). Future gating would be one wildcard rule `github.projectnova.download/public/* → none` + `/* → access_code`.
