from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, Response

from apps import name_svg
from apps.config import get_config

router = APIRouter()

_STATIC = Path(__file__).resolve().parent.parent / "static" / "assets"


def _demo_files() -> list[Path]:
    # Generated at startup by the app lifespan.
    return sorted(p for p in _STATIC.glob("typing_*.svg"))


@router.get("/")
async def root():
    return {"service": "NovaProtocol Assets", "status": "ok"}


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/typing.svg")
async def typing_svg():
    # Serve a single, fixed demo (the full combined animation is non-looping).
    demo_files = _demo_files()
    path = demo_files[0] if demo_files else _STATIC / "typing.svg"
    if not path.exists():
        return JSONResponse({"error": "not found"}, status_code=404)
    return FileResponse(
        path,
        media_type="image/svg+xml",
        headers={"Cache-Control": "no-store, max-age=0"},
    )


@router.get("/name.svg")
async def name_route():
    svg = name_svg.render_name_svg()
    return Response(
        content=svg,
        media_type="image/svg+xml",
        headers={"Cache-Control": "no-store, max-age=0"},
    )


@router.get("/test")
async def test_preview():
    # Debug-only: renders a mock GitHub profile page so the profile can be
    # previewed locally without deploying unfinished work to production.
    if not get_config().DEBUG:
        return JSONResponse({"error": "not found"}, status_code=404)
    from apps import test_page

    return HTMLResponse(test_page.render_test_page())
