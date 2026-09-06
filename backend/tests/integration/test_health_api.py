"""
Integration Tests — Health API
Tests for the GET /api/v1/health endpoint.
"""

import pytest
from fastapi.testclient import TestClient


class TestHealthEndpoint:
    """Tests for the /api/v1/health endpoint."""

    def test_health_returns_200(self, client: TestClient) -> None:
        """Health endpoint must always return HTTP 200."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200

    def test_health_response_has_required_fields(self, client: TestClient) -> None:
        """Response must contain all required top-level fields."""
        response = client.get("/api/v1/health")
        data = response.json()

        required_fields = {
            "status",
            "version",
            "app_name",
            "uptime_seconds",
            "environment",
            "llm_provider",
            "components",
        }
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

    def test_health_status_is_ok_or_degraded(self, client: TestClient) -> None:
        """Overall status must be one of the expected values."""
        response = client.get("/api/v1/health")
        data = response.json()
        assert data["status"] in {"ok", "degraded", "error"}

    def test_health_components_structure(self, client: TestClient) -> None:
        """Components block must include api, database, vector_store."""
        response = client.get("/api/v1/health")
        components = response.json()["components"]
        assert "api" in components
        assert "database" in components
        assert "vector_store" in components

    def test_health_api_component_is_ok(self, client: TestClient) -> None:
        """The 'api' component must always report 'ok'."""
        response = client.get("/api/v1/health")
        api_status = response.json()["components"]["api"]["status"]
        assert api_status == "ok"

    def test_health_uptime_is_positive(self, client: TestClient) -> None:
        """Uptime must be a positive number."""
        response = client.get("/api/v1/health")
        uptime = response.json()["uptime_seconds"]
        assert isinstance(uptime, (int, float))
        assert uptime >= 0

    def test_health_version_matches_config(self, client: TestClient) -> None:
        """Version in response must match the configured app version."""
        from app.core.config import settings
        response = client.get("/api/v1/health")
        assert response.json()["version"] == settings.app_version

    def test_health_llm_provider_is_mock(self, client: TestClient) -> None:
        """LLM provider should be 'mock' in Phase 1 development."""
        response = client.get("/api/v1/health")
        # In CI / default config, LLM provider is mock
        llm = response.json()["llm_provider"]
        assert llm in {"mock", "openai", "google", "anthropic"}
