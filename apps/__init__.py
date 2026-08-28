from __future__ import annotations

import logging
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


def create_app() -> FastAPI:
    config = get_config()

    from pathlib import Path as _Path
    from fastapi.responses import HTMLResponse, JSONResponse
    from fastapi.templating import Jinja2Templates
    from starlette.exceptions import HTTPException as StarletteHTTPException

    _tpl = Jinja2Templates(directory=str(_Path(__file__).resolve().parent.parent / "templates"))
    _titles = {
        400: "Bad Request", 401: "Unauthorized", 403: "Forbidden", 404: "Not Found",
        405: "Method Not Allowed", 408: "Request Timeout", 429: "Too Many Requests",
        500: "Internal Server Error", 502: "Bad Gateway", 503: "Service Unavailable", 504: "Gateway Timeout",
    }

    app = FastAPI(
        title="NovaProtocol Assets",
        description="Public asset server for the NovaProtocol GitHub profile.",
        debug=config.DEBUG,
    )

    @app.exception_handler(StarletteHTTPException)
    async def _http(request, exc: StarletteHTTPException):
        code = exc.status_code if exc.status_code in _titles else 500
        title = _titles.get(code, "Error")
        msg = str(exc.detail) if code != 404 else "The asset you're looking for doesn't exist."
        accept = request.headers.get("accept", "")
        if "application/json" in accept and "text/html" not in accept:
            return JSONResponse({"error": title, "code": code}, status_code=code)
        return _tpl.TemplateResponse(request, "error.html", {"code": code, "title": title, "message": msg}, status_code=code)

    @app.exception_handler(Exception)
    async def _exc(request, exc: Exception):
        if isinstance(exc, StarletteHTTPException):
            return await _http(request, exc)
        return _tpl.TemplateResponse(request, "error.html", {"code": 500, "title": "Internal Server Error", "message": "Something went wrong."}, status_code=500)

    @app.middleware("http")
    async def access_log(request, call_next):
        response = await call_next(request)
        logger.info(
            '%s %s %s "%s"',
            request.client.host if request.client else "-",
            request.method,
            response.status_code,
            request.url.path,
        )
        return response

    static_dir = _PROJECT_ROOT / "static"
    static_dir.mkdir(parents=True, exist_ok=True)
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    from apps.routes import router

    app.include_router(router)

    return app
