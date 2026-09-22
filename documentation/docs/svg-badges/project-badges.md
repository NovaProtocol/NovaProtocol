# Project Badges

Alongside the three profile badges, the app serves a short animated terminal badge per project. They
are embedded in each project's `README.md` and on the project's page in the portfolio.

```markdown
![GateKeeper](https://github.projectnova.download/public/projects/gatekeeper.svg)
```

## Endpoints

| Method | Path | Notes |
|--------|------|-------|
| `GET` | `/public/project/{slug}.svg` | The badge. `image/svg+xml`, `public, max-age=300` plus an `ETag`. `404` for an unknown slug |
| `GET` | `/projects/{slug}.svg` | Legacy short form, `301` to the canonical path |

`GET /public` lists every canonical asset, including one entry per project badge.

## Slugs

| Slug | Project |
|------|---------|
| `gatekeeper` | GateKeeper |
| `water-billing-system` | Water Billing System |
| `mle-review` | MELE Review |
| `practiceforge` | PracticeForge |
| `portfolio` | Portfolio |
| `novaprotocol` | NovaProtocol |

`apps/project_svg.py` owns the sessions. `SESSIONS` maps a slug to the same
`list[dict]` shape the other badges use, and `slugs()` returns them in a stable order so the index
page and the tests agree.

## How the Badge Is Built

The session runs `./get_project_name.sh` and prints the project name as block art, followed by a
one-line description. The art is generated from a real FIGlet font, so nothing is hand-drawn:

```python
"gatekeeper": {
    "art": "GateKeeper",                                  # rendered in the block font
    "blurb": "one login for a family of self-hosted web apps",
    "detail": "signed session cookie, per-path rules, instant revocation",
},
```

- `apps/fonts/ansi_shadow.flf` is the ANSI Shadow FIGlet font, the widely used block style.
- `apps/figlet.py` parses it. It implements only the subset of the FIGlet format this font uses,
  so there is no new dependency.
- `apps/project_svg.py` maps a slug to a name and a sentence, then hands the art to `TerminalSVG`.

The font is 7 rows tall; the last row is the blank shadow baseline that gives the letters their
depth, which is why every glyph sits on six carved rows and one empty one.

## Adding a Badge

1. Add the slug to `SLUGS` and an entry to `PROJECTS` in `apps/project_svg.py`.
2. Add a row to the table above.
3. Embed it with the canonical URL.

No route or template change is needed: the route takes the slug as a path parameter and the index
page enumerates `slugs()`. A name that is longer than about 14 characters will be very wide at this
font size, so keep `art` short.

## Adding a Badge

1. Add the slug and its session to `SESSIONS` in `apps/project_svg.py`.
2. Add a row to the table above.
3. Embed it with the canonical URL.

No route or template change is needed: the route takes the slug as a path parameter and the index
page enumerates `slugs()`.
