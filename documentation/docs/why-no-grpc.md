# Why No gRPC

NovaProtocol has **no gRPC server, no `.proto` files, and no `api:50051`** — by design.

## House Rule (`reference/fastapi/grpc.md`)

> Use gRPC for container-to-container server-side traffic only. The API runs `grpc.aio.server` on `api:50051`; other containers call it with `grpc.aio.insecure_channel("api:50051")`. If you have no server-side container-to-container calls, skip gRPC entirely.

| Traffic | Protocol | Endpoint |
|---------|----------|----------|
| `api:50051` internal (worker→api, portal→api) | gRPC | `grpc.aio.server` |
| Browser / webhook / public via Caddy → api | HTTP | `handle /api/*` + `reverse_proxy api:8008` |

`50051` is `expose:` only, never `ports:`-published, on an `internal: true` network.

## Why NovaProtocol Needs None of It

NovaProtocol is a **single-service monolith** with **no container-to-container calls**:

- One FastAPI monolith (`apps/__init__.py` factory on `novaprotocol_main:7051`) serves every route: `/` , `/health`, `/name.svg`, `/console.svg`, `/skills.svg`, `/test`.
- The `documentation` service (`novaprotocol_documentation:8005`) is read-only MkDocs — stateless, builds at image-build time, serves prebuilt `site/`, never calls the app and is never called by it.
- There is no `api` → `worker` fanout, no `portal` → `api` internal RPC, no shared DB sharding that would benefit from typed protos or streaming.
- The only integration is **Caddy → app HTTP** over the compose `default` network — `reverse_proxy novaprotocol_main:7051` with the original path. That traffic is HTTP by contract; gRPC over HTTP/2 would require a dedicated gRPC gateway that the house Caddy does not do.
- All rendering is in-process — `apps/name_svg.py`, `apps/console_svg.py`, `apps/skills_svg.py` call `utilities/terminal_svg` directly. No network hop.

Adding a `grpc.aio.server` on `:50051` would:

- Require `grpcio`, `grpcio-tools`, `protobuf` in `requirements.txt` (`grpcio>=1.60,<2`, `protobuf>=4,<7`) with no caller.
- Introduce `.proto` compilation (`shared/proto/`, `proto_gen/`) and a stub that nothing imports.
- Publish `expose: ["50051"]` that is never probed — noise in compose and docs.
- Duplicate logic: the SVG renderers would be exposed over two transports for zero benefit.

## What We Document Instead

- **HTTP is the only contract:** public `GET` routes via Caddy (see [API Reference](api-reference.md)).
- **No service token**, no `X-Internal-API-Key`, no `API_INTERNAL_URL` / `API_GRPC_ADDR` — those vars belong to multi-service systems (WBS, SolveSpace).
- The `utilities/terminal_svg` library is consumed as a Python import, not a network service.

## What a Future Split Would Look Like

If this monolith ever grows a second container that needs server-side calls (e.g., a sidecar stats aggregator that tail-calls the app for SVG metrics, or a separate renderer worker), the addition would be:

- `shared/proto/api.proto` + `shared/proto_gen/` (generated stubs)
- `grpc.aio.server` on `api:50051` started in the API's lifespan (see `reference/fastapi/grpc.md` lifespan pattern)
- `grpc.aio.insecure_channel("api:50051")` from the worker/portal on `internal: true` `net-api`
- `expose: ["50051"]` only (never `ports:`), business logic in `*_service.py` called by both HTTP and gRPC

Until then, this page is the evidence that **no gRPC** is the correct, documented decision — not an omission.

## Comparison: When gRPC Is Required

| System | Needs gRPC | Reason |
|--------|------------|--------|
| NovaProtocol | **No** — monolith, HTTP only | All rendering in-process, one app + caddy + docs |
| BuddysFreelanceProject | **No** — monolith | Same reason — `data/` inside the app, Caddy → app HTTP |
| GateKeeper | **No** — single Flask monolith | One `app.py` serves every route; docs is stateless |
| WaterBillingSystem | **Yes** | `worker`/`portal`/`webhook` → `api:50051` over `net-api` |
| SolveSpace `executor/` | **Yes** | `api` → `executor:50051` (sandbox) |

```
[Internet] --HTTP--> [Caddy :7050] --HTTP--> [novaprotocol_main:7051 FastAPI]
[documentation :8005] (no RPC to app)
(no gRPC, no internal API)
```
