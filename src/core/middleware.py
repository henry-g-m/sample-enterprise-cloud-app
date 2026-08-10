"""Request/response middleware and utilities."""

import time
from collections.abc import Awaitable, Callable

import structlog
from fastapi import FastAPI, Request
from fastapi.responses import Response

logger = structlog.get_logger(__name__)


async def request_logging_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Middleware to log HTTP requests and responses."""
    start_time = time.time()

    # Add request ID to context
    request_id = request.headers.get("x-request-id", "")

    try:
        response = await call_next(request)
        duration_ms = (time.time() - start_time) * 1000

        logger.info(
            "http_request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
            request_id=request_id,
        )

        return response
    except Exception as exc:
        duration_ms = (time.time() - start_time) * 1000
        logger.exception(
            "http_request_error",
            method=request.method,
            path=request.url.path,
            duration_ms=round(duration_ms, 2),
            request_id=request_id,
            error=str(exc),
        )
        raise


def add_request_logging_middleware(app: FastAPI) -> None:
    """Add request logging middleware to FastAPI app."""
    app.middleware("http")(request_logging_middleware)
