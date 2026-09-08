from __future__ import annotations

import logging
import uuid

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.templating import Jinja2Templates

try:
    import structlog  # type: ignore

    _HAS_STRUCTLOG = True
except ImportError:
    _HAS_STRUCTLOG = False


def _request_id(request: Request) -> str:
    return getattr(request.state, "request_id", None) or request.headers.get("X-Request-ID") or uuid.uuid4().hex


def _log(level: str, event: str, request: Request, **kw):
    rid = _request_id(request)
    extra = {"request_id": rid, "path": request.url.path, "method": request.method, **kw}
    if _HAS_STRUCTLOG:
        try:
            logger = structlog.get_logger("novaprotocol")
            getattr(logger, level)(event, **extra)
            return rid
        except Exception:
            pass
    logging.getLogger("novaprotocol").log(getattr(logging, level.upper(), logging.INFO), "%s %s", event, extra)
    return rid


def _envelope(code: str, message: str, request_id: str, details=None):
    body = {"error": {"code": code, "message": message, "request_id": request_id}}
    if details is not None:
        body["error"]["details"] = details
    return body


_TITLES = {
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    408: "Request Timeout",
    429: "Too Many Requests",
    500: "Internal Server Error",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
}


def install_error_handlers(app, templates: Jinja2Templates):
    async def _http(request: Request, exc: StarletteHTTPException):
        rid = _request_id(request)
        code = exc.status_code if exc.status_code in _TITLES else 500
        title = _TITLES.get(code, "Error")
        msg = str(exc.detail) if code != 404 else "The page you\'re looking for doesn\'t exist."
        if code >= 500:
            _log("error", "http_exception", request, status_code=code, error_code=title)
        else:
            _log("warning", "http_error", request, status_code=code, error_code=title)
        accept = request.headers.get("accept", "")
        if "application/json" in accept and "text/html" not in accept:
            return JSONResponse(_envelope(title.replace(" ", "_").upper(), msg, rid), status_code=code, headers={"X-Request-ID": rid})
        return templates.TemplateResponse(request, "error.html", {"code": code, "title": title, "message": msg}, status_code=code, headers={"X-Request-ID": rid})

    async def _val(request: Request, exc: RequestValidationError):
        rid = _request_id(request)
        _log("warning", "validation_error", request, status_code=400, error_code="VALIDATION_ERROR")
        details = [{"loc": e.get("loc"), "msg": e.get("msg"), "type": e.get("type")} for e in exc.errors()]
        return JSONResponse(_envelope("VALIDATION_ERROR", "Validation failed", rid, details=details), status_code=400, headers={"X-Request-ID": rid})

    async def _gen(request: Request, exc: Exception):
        rid = _request_id(request)
        _log("error", "unhandled_exception", request, status_code=500, error_code="INTERNAL_ERROR")
        accept = request.headers.get("accept", "")
        if "application/json" in accept and "text/html" not in accept:
            return JSONResponse(_envelope("INTERNAL_ERROR", "Internal server error", rid), status_code=500, headers={"X-Request-ID": rid})
        return templates.TemplateResponse(request, "error.html", {"code": 500, "title": "Internal Server Error", "message": "Something went wrong."}, status_code=500, headers={"X-Request-ID": rid})

    app.add_exception_handler(StarletteHTTPException, _http)
    app.add_exception_handler(RequestValidationError, _val)
    app.add_exception_handler(Exception, _gen)
