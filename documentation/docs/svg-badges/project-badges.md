# Project Badges

Alongside the three profile badges, the app serves a short animated terminal badge per project. They
are embedded in each project's `README.md` and on the project's page in the portfolio.

```markdown
![GateKeeper](https://github.projectnova.download/public/projects/gatekeeper.svg)
```

## Endpoints

| Method | Path | Notes |
|--------|------|-------|
| `GET` | `/public/projects/{slug}.svg` | The badge. `image/svg+xml`, `no-store`. `404` for an unknown slug |
| `GET` | `/projects/{slug}.svg` | Legacy short form, `301` to the canonical path |

`GET /public` lists every canonical asset, including one entry per project badge.

## Slugs

| Slug | Project |
|------|---------|
| `gatekeeper` | GateKeeper |
| `water-billing-system` | Water Billing System |
| `mle-review` | MELE Review |
| `solvespace` | SolveSpace |
| `portfolio` | Portfolio |
| `novaprotocol` | NovaProtocol |

`apps/project_svg.py` owns the sessions. `SESSIONS` maps a slug to the same
`list[dict]` shape the other badges use, and `slugs()` returns them in a stable order so the index
page and the tests agree.

## Writing a Session

A session shows the project **doing its job** rather than listing the technology it is built with.
Each entry is an `input` the reader can follow and the `output` that results, so the badge reads as a
demonstration instead of a claim:

```python
"water-billing-system": [
    {
        "input": "billing read --meter 10023 --value 1284",
        "output": [
            f"{GRAY}computing password on device, no network needed{RESET}",
            f"{GREEN}reading recorded{RESET} {GRAY}meter=10023 value=1284 m3{RESET}",
        ],
    },
]
```

Keep sessions to three entries or fewer. A badge is glanced at, and an animation that runs long is
worse than no animation.

## Adding a Badge

1. Add the slug and its session to `SESSIONS` in `apps/project_svg.py`.
2. Add a row to the table above.
3. Embed it with the canonical URL.

No route or template change is needed: the route takes the slug as a path parameter and the index
page enumerates `slugs()`.
