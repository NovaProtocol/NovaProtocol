# Documentation

Full project documentation for **NovaProtocol**, built with [MkDocs](https://www.mkdocs.org/) and the Material theme.

## Contents

| Section | Description |
|---------|-------------|
| [Home](./docs/index.md) | Overview and service map |
| [Getting Started](./docs/getting-started.md) | Prerequisites and local startup |
| [Architecture](./docs/architecture.md) | Monolith topology, factory, routing, data |
| [Terminal SVG](./docs/terminal-svg/index.md) | Animated terminal library — ANSI, timeline, rendering |
| [SVG Badges](./docs/svg-badges/index.md) | name.svg / console.svg / skills.svg generation |
| [API Reference](./docs/api-reference.md) | HTTP routes and SVG endpoints |
| [Docker](./docs/docker.md) | Compose, Caddy, and deployment |
| [Why No gRPC](./docs/why-no-grpc.md) | Why this monolith has no gRPC |

## Building Locally

```bash
pip install -r requirements.txt
mkdocs build
mkdocs serve    # preview at http://localhost:8000
```

Served in production as a FastAPI container (`app.py` on `:8005`) behind Caddy at `/documentation/` (public, no GateKeeper gate).
