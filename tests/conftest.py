"""Pytest configuration and shared fixtures."""

import pytest
from fastapi.testclient import TestClient

from src.app import create_app


@pytest.fixture(scope="session")
def app():
    """Create and yield FastAPI application for tests."""
    test_app = create_app()
    yield test_app


@pytest.fixture
def client(app):
    """Provide test client for FastAPI app."""
    return TestClient(app)
