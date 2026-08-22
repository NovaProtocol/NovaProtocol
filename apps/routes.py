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


@router.get("/test")
async def test_preview():
    from apps import test_page

    return HTMLResponse(test_page.render_test_page())
