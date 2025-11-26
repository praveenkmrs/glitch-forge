"""Tests for main application endpoints.

This demonstrates production-ready testing practices:
1. Using TestClient for API testing
2. Async test support
3. Clear test structure (Arrange, Act, Assert)
"""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint returns correct status."""
    # Act
    response = client.get("/health")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "environment" in data


def test_root_endpoint():
    """Test root endpoint returns welcome message."""
    # Act
    response = client.get("/")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_cors_headers():
    """Test CORS headers are properly configured."""
    # Act
    response = client.options(
        "/health",
        headers={"Origin": "http://localhost:3000"},
    )

    # Assert - CORS headers should be present
    assert "access-control-allow-origin" in response.headers
