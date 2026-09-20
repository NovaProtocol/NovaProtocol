from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, RedirectResponse, Response

from apps import console_svg, name_svg, project_svg, skills_svg

router = APIRouter()

_NO_CACHE = {"Cache-Control": "no-store, max-age=0"}


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
async def public_name_route():
    return Response(
        content=name_svg.render_name_svg(),
        media_type="image/svg+xml",
        headers=_NO_CACHE,
    )


@router.get("/public/console.svg")
async def public_console_route():
    return Response(
        content=console_svg.render_console_svg(),
        media_type="image/svg+xml",
        headers=_NO_CACHE,
    )


@router.get("/public/skills.svg")
async def public_skills_route():
    return Response(
        content=skills_svg.render_skills_svg(),
        media_type="image/svg+xml",
        headers=_NO_CACHE,
    )


@router.get("/public/project/{slug}.svg")
async def public_project_route(slug: str):
    try:
        content = project_svg.render_project_badge(slug)
    except KeyError:
        return Response(
            content=f"no badge for {slug!r}",
            media_type="text/plain",
            status_code=404,
        )
    return Response(
        content=content,
        media_type="image/svg+xml",
        headers=_NO_CACHE,
    )

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
