"""Request/response middleware and utilities."""

import time
import uuid
from collections.abc import Awaitable, Callable

import structlog
from fastapi import FastAPI, Request
from fastapi.responses import Response

from src.infrastructure.observability.metrics import get_metrics

logger = structlog.get_logger(__name__)


async def request_logging_middleware(
    request: Request, call_next: Callable[[Request], Awaitable[Response]]
) -> Response:
    """Log HTTP requests/responses, record metrics, and propagate a correlation ID.

    The request ID is taken from an incoming `x-request-id` header or
    generated fresh, then bound to structlog's contextvars for the lifetime
    of the request so every log line emitted while handling it - not just
    the ones below - carries the same request_id, and echoed back in the
    response header for the caller to correlate against.
    """
    start_time = time.time()
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    metrics = get_metrics()

    structlog.contextvars.bind_contextvars(request_id=request_id)
    try:
        try:
            response = await call_next(request)
        except Exception as exc:
            duration_ms = (time.time() - start_time) * 1000
            logger.exception(
                "http_request_error",
                method=request.method,
                path=request.url.path,
                duration_ms=round(duration_ms, 2),
                error=str(exc),
            )
            metrics.http_requests_total.add(
                1, {"method": request.method, "path": request.url.path, "status_code": 500}
            )
            metrics.http_request_duration_seconds.record(
                (time.time() - start_time), {"method": request.method, "path": request.url.path}
            )
            raise

        duration_ms = (time.time() - start_time) * 1000
        logger.info(
            "http_request",
            method=request.method,
            path=request.url.path,
            status_code=response.status_code,
            duration_ms=round(duration_ms, 2),
        )
        metrics.http_requests_total.add(
            1,
            {
                "method": request.method,
                "path": request.url.path,
                "status_code": response.status_code,
            },
        )
        metrics.http_request_duration_seconds.record(
            (time.time() - start_time), {"method": request.method, "path": request.url.path}
        )

        response.headers["x-request-id"] = request_id
        return response
    finally:
        structlog.contextvars.unbind_contextvars("request_id")


def add_request_logging_middleware(app: FastAPI) -> None:
    """Add request logging middleware to FastAPI app."""
    app.middleware("http")(request_logging_middleware)
