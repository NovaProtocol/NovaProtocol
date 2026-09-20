from __future__ import annotations

import logging
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from apps.config import get_config

try:
    import structlog  # type: ignore

    _HAS_STRUCTLOG = True
except ImportError:
    _HAS_STRUCTLOG = False

_PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _configure_logging() -> None:
    if _HAS_STRUCTLOG:
        try:
            import structlog

            structlog.configure(
                processors=[
                    structlog.contextvars.merge_contextvars,
                    structlog.processors.add_log_level,
                    structlog.processors.TimeStamper(fmt="iso"),
                    structlog.processors.JSONRenderer(),
                ],
                wrapper_class=structlog.make_filtering_bound_logger(logging.NOTSET),
                context_class=dict,
                logger_factory=structlog.PrintLoggerFactory(file=sys.stdout),
                cache_logger_on_first_use=True,
            )
        except Exception:
            pass
    # The access-log middleware logs through the stdlib root logger, so it needs
    # a handler whichever branch configured structlog. Without this the service
    # serves requests silently and there is no way to see what it was asked for.
    logging.basicConfig(level=logging.INFO, format="%(message)s", stream=sys.stdout)
    if _HAS_STRUCTLOG:
        return


def create_app() -> FastAPI:
    _configure_logging()
    config = get_config()

    app = FastAPI(
        title="NovaProtocol Assets",
        description="Public asset server for the NovaProtocol GitHub profile.",
        debug=config.DEBUG,
    )

    from apps.middleware import RequestIDMiddleware

    app.add_middleware(RequestIDMiddleware)

    # optional access log (keep original behaviour via middleware already)
    @app.middleware("http")
    async def _access_log(request, call_next):
        response = await call_next(request)
        logging.getLogger("access").info(
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

    # error handlers need templates, use app's Jinja2Templates from routes if available, else create
    try:
        from pathlib import Path as _P
        from fastapi.templating import Jinja2Templates
        _tpl = Jinja2Templates(directory=str(_P(__file__).resolve().parent.parent / "templates"))
        from apps.errors import install_error_handlers

        install_error_handlers(app, _tpl)
    except Exception:
        pass

    return app
