# Getting Started

## Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Docker & Docker Compose | Latest | Production stack (recommended) |
| Python | `3.14` (`.python-version`) | Local dev |
| `pip` / `venv` | stdlib | Dependency install |

---

## 1. Clone & Configure

```bash
git clone https://github.com/NovaProtocol/NovaProtocol
cd NovaProtocol
```

Environment variables are injected by compose interpolation. Full list in `.env.example`:

| Variable | Required | Description |
|----------|----------|-------------|
| `DEPLOYMENT_TYPE` | yes | `debug` or `production` (controls `FastAPI(debug=…)` and `uvicorn --reload`) |

```bash
export DEPLOYMENT_TYPE=debug   # or production
```

> No `.env` file is used. Compose fails fast with `${VAR:?}` if `DEPLOYMENT_TYPE` is unset. App config reads strictly from `os.environ`.

---

## 2. Run Locally (dev)

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt -r requirements-dev.txt
export DEPLOYMENT_TYPE=debug
.venv/bin/python run.py            # uvicorn :8000, reload in debug
```

- Dev server: `http://127.0.0.1:8000/` and `http://127.0.0.1:8000/health`
- Badge previews: `http://127.0.0.1:8000/name.svg`, `/console.svg`, `/skills.svg`
- Live gallery: `http://127.0.0.1:8000/test` — embeds all three SVGs via `<object>` so SMIL runs.
- `run.py` sets `os.environ["DEPLOYMENT_TYPE"]` from `--mode` and runs `uvicorn "apps:create_app" factory=True`.

---

## 3. Run in Docker (prod parity)

```bash
export DEPLOYMENT_TYPE=production
docker compose up -d --build
docker compose ps
docker compose logs -f app
```

| URL | What |
|-----|------|
| `http://localhost:7050/` (via tunnel) | Public app — `GET /health` and the three SVGs are public |
| `http://localhost:7050/health` | Health bypass (Caddy `handle /health`) |
| `http://localhost:7050/documentation/` | MkDocs site — **public** (`handle_path /documentation/*` without `forward_auth`) |
| `http://app:8000/health` (inside network) | Direct app health (compose healthcheck) |
| `http://documentation:8005/health` (inside network) | Docs healthcheck |

First build installs `requirements.txt` (FastAPI, granian, svgwrite) and `documentation/requirements.txt` (MkDocs) then runs `mkdocs build` inside the docs image.

---

## 4. MkDocs Site Alone

```bash
pip install -r documentation/requirements.txt
mkdocs build --config-file documentation/mkdocs.yml
mkdocs serve --config-file documentation/mkdocs.yml  # http://127.0.0.1:8000
```

Inside Docker, the docs container serves prebuilt `site/` via FastAPI + granian:

```bash
docker compose up -d --build documentation
curl -s http://127.0.0.1:8005/health  # via sibling container: {"status":"ok"}
# or through Caddy:
curl -s http://127.0.0.1:7050/documentation/ | head
```

---

## 5. Quick Reference

```bash
# Validate compose interpolations without starting
docker compose config > /dev/null

# Rebuild just the app after a route change
docker compose up -d --build app

# Rebuild just the docs after editing documentation/docs/
docker compose up -d --build documentation

# Check pre-commit locally
pip install pre-commit
pre-commit run --all

# Run tests
pytest -q
```

---

## 6. Embedding the Badges

The profile README (`README.md`) embeds the live badges:

```markdown
![name](https://github.projectnova.download/name.svg)
![skills](https://github.projectnova.download/skills.svg)
![console](https://github.projectnova.download/console.svg)
```

Each endpoint returns `image/svg+xml` with `Cache-Control: no-store, max-age=0` so GitHub's camo proxy does not stale-cache the animation. The SVG itself carries SMIL `<animate>` timing — no JavaScript is needed and none runs in the README context.

To test locally, open `http://127.0.0.1:8000/test` — it renders the same three objects the profile does, but against your running app.
