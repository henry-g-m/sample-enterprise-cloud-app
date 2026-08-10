"""Pytest configuration and shared fixtures."""

import pytest
from fastapi.testclient import TestClient

from src.app import create_app
from src.infrastructure.cache.redis_client import close_redis_client


@pytest.fixture(scope="session")
def app():
    """Create and yield FastAPI application for tests."""
    test_app = create_app()
    yield test_app


@pytest.fixture
def client(app):
    """Provide test client for FastAPI app."""
    return TestClient(app)


@pytest.fixture(autouse=True)
async def _reset_redis_client():
    """Close the Redis singleton after every test.

    Its connection pool is bound to the event loop it was created in, and
    pytest-asyncio opens a fresh loop per test function, so a pool left open
    from a previous test raises "Event loop is closed" on reuse. Closing it
    here forces a lazy, fresh reconnect in whichever loop the next test runs.
    """
    yield
    await close_redis_client()
