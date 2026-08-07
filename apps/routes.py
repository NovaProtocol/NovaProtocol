from __future__ import annotations

import random
from pathlib import Path

from fastapi import APIRouter
from fastapi.responses import FileResponse

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
    # Randomly pick a demo SVG per request so each page load shows a
    # different looping animation.
    demo_files = _demo_files()
    if demo_files:
        path = random.choice(demo_files)
    else:
        path = _STATIC / "typing.svg"
    if not path.exists():
        from fastapi.responses import JSONResponse

        return JSONResponse({"error": "not found"}, status_code=404)
    # no-store so Cloudflare does not cache it and the request always hits
    # this server (and shows up in the access logs)
    return FileResponse(
        path,
        media_type="image/svg+xml",
        headers={"Cache-Control": "no-store, max-age=0"},
    )
