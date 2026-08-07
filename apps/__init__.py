from __future__ import annotations

import logging
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from apps.config import get_config

logger = logging.getLogger("access")
logger.setLevel(logging.INFO)
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    logger.addHandler(handler)
    logger.propagate = False

_PROJECT_ROOT = Path(__file__).resolve().parent.parent


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Generate the demo SVGs at startup (they are gitignored, not committed).
    assets = _PROJECT_ROOT / "static" / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    if not list(assets.glob("typing_*.svg")):
        scripts_dir = _PROJECT_ROOT / "scripts"
        if str(scripts_dir) not in sys.path:
            sys.path.insert(0, str(scripts_dir))
        try:
            import make_svg

            make_svg.generate()
        except Exception as exc:  # pragma: no cover
            logger.error("failed to generate typing SVGs: %s", exc)
    yield


def create_app() -> FastAPI:
    config = get_config()

    app = FastAPI(
        title="NovaProtocol Assets",
        description="Public asset server for the NovaProtocol GitHub profile.",
        debug=config.DEBUG,
        lifespan=lifespan,
    )

    @app.middleware("http")
    async def access_log(request, call_next):
        response = await call_next(request)
        logger.info('%s %s %s "%s"', request.client.host if request.client else "-", request.method, response.status_code, request.url.path)
        return response

    static_dir = _PROJECT_ROOT / "static"
    static_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    from apps.routes import router

    app.include_router(router)

    return app
