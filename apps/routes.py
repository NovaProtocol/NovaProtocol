from __future__ import annotations

import hashlib

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from apps import console_svg, name_svg, project_svg, skills_svg

router = APIRouter()

# The SVGs are re-rendered on every request and their bytes change whenever the
# art, the blurbs, or the font change. Instead of forbidding caches outright, the
# response carries an ETag derived from the bytes, so a cache stores the render
# and revalidates it cheaply:
#
#   unchanged -> 304 Not Modified, a few bytes, no re-render sent
#   changed   -> 200 with the new bytes
#
# That gives a cached response for speed without a manual purge step, because the
# cache is told when the content moves rather than assuming it never will.
#
# `public` is what lets Cloudflare and camo store it: a `private` response is
# skipped by every shared cache. The window is deliberately short (5 minutes), so
# a change becomes visible quickly even if a cache never revalidates; the ETag
# below makes the revalidation cheap when the cache does ask.
_SVG_CACHE = {"Cache-Control": "public, max-age=300"}


def _etag(body: bytes) -> str:
    """Strong ETag over the rendered bytes."""
    return '"' + hashlib.sha256(body).hexdigest()[:32] + '"'


def _svg_response(body: bytes, request: Request) -> Response:
    """Return the SVG with a cache policy that revalidates on change.

    A matching `If-None-Match` answers `304` with no body, which is what makes a
    cached badge cheap while still updating the moment the content differs.
    """
    tag = _etag(body)
    if request.headers.get("if-none-match") == tag:
        return Response(status_code=304, headers={**_SVG_CACHE, "ETag": tag})
    return Response(
        content=body,
        media_type="image/svg+xml",
        headers={**_SVG_CACHE, "ETag": tag},
    )


@router.get("/")
async def root():
    return {"service": "NovaProtocol Assets", "status": "ok"}


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/name.svg", include_in_schema=False)
async def name_route():
    return RedirectResponse(url="/public/name.svg", status_code=301)


@router.get("/console.svg", include_in_schema=False)
async def console_route():
    return RedirectResponse(url="/public/console.svg", status_code=301)


@router.get("/skills.svg", include_in_schema=False)
async def skills_route():
    return RedirectResponse(url="/public/skills.svg", status_code=301)


@router.get("/projects/{slug}.svg", include_in_schema=False)
async def project_route(slug: str):
    return RedirectResponse(url=f"/public/project/{slug}.svg", status_code=301)

@router.get("/public/name.svg")
async def public_name_route(request: Request):
    return _svg_response(name_svg.render_name_svg().encode("utf-8"), request)


@router.get("/public/console.svg")
async def public_console_route(request: Request):
    return _svg_response(console_svg.render_console_svg().encode("utf-8"), request)


@router.get("/public/skills.svg")
async def public_skills_route(request: Request):
    return _svg_response(skills_svg.render_skills_svg().encode("utf-8"), request)


@router.get("/public/project/{slug}.svg")
async def public_project_route(slug: str, request: Request):
    try:
        content = project_svg.render_project_badge(slug)
    except KeyError:
        return Response(
            content=f"no badge for {slug!r}",
            media_type="text/plain",
            status_code=404,
        )
    return _svg_response(content.encode("utf-8"), request)

@router.get("/public/projects/{slug}.svg", include_in_schema=False)
async def project_plural_route(slug: str):
    """The plural path an earlier revision served. Redirect, never 404."""
    return RedirectResponse(url=f"/public/project/{slug}.svg", status_code=301)

@router.get("/public")
async def public_index():
    badges = "".join(
        f"<li><a href='/public/project/{slug}.svg'>/public/project/{slug}.svg</a></li>"
        for slug in project_svg.slugs()
    )
    body = (
        "<html><head><title>Public assets</title></head>"
        "<body style='font-family:monospace;padding:2rem'>"
        "<h1>Public assets</h1><ul>"
        "<li><a href='/public/name.svg'>/public/name.svg</a></li>"
        "<li><a href='/public/skills.svg'>/public/skills.svg</a></li>"
        "<li><a href='/public/console.svg'>/public/console.svg</a></li>"
        f"{badges}"
        "</ul>"
        "<p>Canonical prefix is "
        "<code>https://github.projectnova.download/public/*.svg</code> for GitHub "
        "embeds. Legacy <code>/name.svg</code> etc. 301 to <code>/public/*.svg</code>."
        "</p>"
        "<script src='/static/js/error.js'></script></body></html>"
    )
    return HTMLResponse(body)

@router.get("/test")
async def test_preview():
    from apps import test_page

    return HTMLResponse(test_page.render_test_page())
