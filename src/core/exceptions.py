"""Custom application exceptions and FastAPI exception handlers."""

import uuid
from typing import Any

import structlog
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = structlog.get_logger(__name__)


class AppException(Exception):
    """Base class for application-specific errors with an HTTP mapping."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "internal_error"

    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        self.message = message
        self.details = details
        super().__init__(message)


class NotFoundError(AppException):
    """Raised when a requested resource does not exist."""

    status_code = status.HTTP_404_NOT_FOUND
    error_code = "not_found"


class ServiceUnavailableError(AppException):
    """Raised when a required downstream dependency is unavailable."""

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    error_code = "service_unavailable"


def _error_response(
    request: Request,
    *,
    status_code: int,
    error_code: str,
    message: str,
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    """Build the standard error envelope shared by every handler."""
    # Prefer the ID request_logging_middleware bound for this request so it
    # matches the access log line; fall back to the header (or a fresh one)
    # for callers that reach a handler without going through that middleware.
    bound_request_id = structlog.contextvars.get_contextvars().get("request_id")
    request_id = bound_request_id or request.headers.get("x-request-id") or str(uuid.uuid4())
    error_body: dict[str, Any] = {
        "code": error_code,
        "message": message,
        "request_id": request_id,
    }
    if details:
        error_body["details"] = details
    return JSONResponse(status_code=status_code, content={"error": error_body})


async def app_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle application-raised errors with a consistent error envelope."""
    assert isinstance(exc, AppException)
    logger.warning(
        "app_exception",
        error_code=exc.error_code,
        message=exc.message,
        path=request.url.path,
    )
    return _error_response(
        request,
        status_code=exc.status_code,
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details,
    )


async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Wrap FastAPI/Starlette HTTPExceptions in the standard error envelope."""
    assert isinstance(exc, StarletteHTTPException)
    return _error_response(
        request,
        status_code=exc.status_code,
        error_code="http_error",
        message=str(exc.detail),
    )


async def validation_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Return request validation failures in the standard error envelope."""
    assert isinstance(exc, RequestValidationError)
    return _error_response(
        request,
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        error_code="validation_error",
        message="Request validation failed",
        details={"errors": exc.errors()},
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all handler that logs the traceback and hides internals from clients."""
    logger.exception("unhandled_exception", path=request.url.path)
    return _error_response(
        request,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code="internal_error",
        message="An unexpected error occurred",
    )


def register_exception_handlers(app: FastAPI) -> None:
    """Register all exception handlers on the FastAPI app."""
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
