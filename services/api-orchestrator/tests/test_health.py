import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from app.dependencies import get_engine
from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


@pytest.mark.unit
def test_health_returns_200_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.unit
def test_health_ready_returns_200_when_db_reachable(client):
    app.dependency_overrides[get_engine] = lambda: create_engine("sqlite:///:memory:")
    try:
        response = client.get("/health/ready")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
    finally:
        app.dependency_overrides.clear()


@pytest.mark.unit
def test_health_ready_returns_503_when_db_unreachable(client):
    class _BrokenEngine:
        def connect(self):
            raise RuntimeError("connection refused")

    app.dependency_overrides[get_engine] = lambda: _BrokenEngine()
    try:
        response = client.get("/health/ready")
        assert response.status_code == 503
    finally:
        app.dependency_overrides.clear()
