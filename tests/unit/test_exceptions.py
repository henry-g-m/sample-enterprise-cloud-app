"""Unit tests for custom exceptions and their FastAPI handlers."""

import json

from fastapi import status
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request

from src.core.exceptions import (
    AppException,
    NotFoundError,
    ServiceUnavailableError,
    app_exception_handler,
    http_exception_handler,
    unhandled_exception_handler,
    validation_exception_handler,
)


def _make_request(headers: dict[str, str] | None = None) -> Request:
    """Build a minimal Request for handler tests."""
    raw_headers = [(key.lower().encode(), value.encode()) for key, value in (headers or {}).items()]
    scope = {
        "type": "http",
        "method": "GET",
        "path": "/api/v1/test",
        "headers": raw_headers,
    }
    return Request(scope)


class TestAppExceptionSubclasses:
    """Test the built-in AppException subclasses map to the right HTTP status."""

    def test_not_found_error_defaults(self):
        exc = NotFoundError("missing")

        assert exc.status_code == status.HTTP_404_NOT_FOUND
        assert exc.error_code == "not_found"
        assert exc.message == "missing"

    def test_service_unavailable_defaults(self):
        exc = ServiceUnavailableError("down")

        assert exc.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert exc.error_code == "service_unavailable"


class TestAppExceptionHandler:
    """Test the handler for application-raised AppException errors."""

    async def test_returns_mapped_status_and_envelope(self):
        request = _make_request()
        exc = NotFoundError("Widget not found", details={"widget_id": "abc"})

        response = await app_exception_handler(request, exc)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        body = json.loads(response.body)
        assert body["error"]["code"] == "not_found"
        assert body["error"]["message"] == "Widget not found"
        assert body["error"]["details"] == {"widget_id": "abc"}
        assert "request_id" in body["error"]

    async def test_uses_incoming_request_id(self):
        request = _make_request({"x-request-id": "req-42"})
        exc = AppException("boom")

        response = await app_exception_handler(request, exc)

        body = json.loads(response.body)
        assert body["error"]["request_id"] == "req-42"


class TestHttpExceptionHandler:
    """Test the handler wrapping Starlette/FastAPI HTTPExceptions."""

    async def test_wraps_http_exception(self):
        request = _make_request()
        exc = StarletteHTTPException(status_code=404, detail="Not Found")

        response = await http_exception_handler(request, exc)

        assert response.status_code == 404
        body = json.loads(response.body)
        assert body["error"]["code"] == "http_error"
        assert body["error"]["message"] == "Not Found"


class TestValidationExceptionHandler:
    """Test the handler for request validation failures."""

    async def test_returns_422_with_errors(self):
        request = _make_request()
        exc = RequestValidationError(
            errors=[{"loc": ("body", "name"), "msg": "field required", "type": "missing"}]
        )

        response = await validation_exception_handler(request, exc)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        body = json.loads(response.body)
        assert body["error"]["code"] == "validation_error"
        assert body["error"]["details"]["errors"]


class TestUnhandledExceptionHandler:
    """Test the catch-all handler for unexpected exceptions."""

    async def test_hides_internal_details(self):
        request = _make_request()
        exc = RuntimeError("db connection string leaked")

        response = await unhandled_exception_handler(request, exc)

        assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        body = json.loads(response.body)
        assert body["error"]["code"] == "internal_error"
        assert "leaked" not in body["error"]["message"]
