from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse, Response

from apps import console_svg, name_svg, skills_svg

router = APIRouter()

_NO_CACHE = {"Cache-Control": "no-store, max-age=0"}


@router.get("/")
async def root():
    return {"service": "NovaProtocol Assets", "status": "ok"}


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/name.svg")
async def name_route():
    return Response(
        content=name_svg.render_name_svg(),
        media_type="image/svg+xml",
        headers=_NO_CACHE,
    )


@router.get("/console.svg")
async def console_route():
    return Response(
        content=console_svg.render_console_svg(),
        media_type="image/svg+xml",
        headers=_NO_CACHE,
    )


@router.get("/skills.svg")
async def skills_route():
    return Response(
        content=skills_svg.render_skills_svg(),
        media_type="image/svg+xml",
        headers=_NO_CACHE,
    )


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


@router.get("/public")
async def public_index():
    return HTMLResponse(
        "<html><head><title>Public assets</title></head><body style='font-family:monospace;padding:2rem'>"
        "<h1>Public assets</h1><ul>"
        "<li><a href='/public/name.svg'>/public/name.svg</a></li>"
        "<li><a href='/public/skills.svg'>/public/skills.svg</a></li>"
        "<li><a href='/public/console.svg'>/public/console.svg</a></li>"
        "</ul><p>Also available at <code>/name.svg</code> etc. Use <code>https://github.projectnova.download/public/*.svg</code> for GitHub embeds.</p>"
        "</body></html>"
    )


@router.get("/test")
async def test_preview():
    from apps import test_page

    return HTMLResponse(test_page.render_test_page())
