"""Integration tests for API endpoints."""

import pytest


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_liveness_returns_200(self, client):
        """Test liveness probe returns 200 with correct structure."""
        response = client.get("/api/v1/health/live")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "alive"
        assert "timestamp" in data
        assert "version" in data

    def test_readiness_returns_200(self, client):
        """Test readiness probe returns 200."""
        response = client.get("/api/v1/health/ready")

        assert response.status_code == 200
        data = response.json()
        assert data["ready"] is True
        assert "timestamp" in data
        assert "dependencies" in data

    def test_startup_returns_200(self, client):
        """Test startup probe returns 200."""
        response = client.get("/api/v1/health/startup")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "started"
        assert "version" in data


class TestAboutEndpoint:
    """Test about endpoint."""

    def test_about_returns_200(self, client):
        """Test about endpoint returns 200 with application info."""
        response = client.get("/api/v1/about")

        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Enterprise Demo Cloud App"
        assert data["version"] == "0.1.0"
        assert "description" in data
        assert "timestamp" in data
        assert "environment" in data

    def test_about_response_structure(self, client):
        """Test about response has required fields."""
        response = client.get("/api/v1/about")

        data = response.json()
        required_fields = ["name", "version", "description", "timestamp", "environment"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
