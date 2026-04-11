from unittest.mock import AsyncMock, patch
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import verify_firebase_token

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def mock_auth():
    async def override_auth():
        return {"uid": "admin123", "name": "Admin", "email": "admin@example.com"}
    app.dependency_overrides[verify_firebase_token] = override_auth
    yield
    app.dependency_overrides.pop(verify_firebase_token, None)

def test_sync_status(client):
    with patch("app.routers.admin.get_sync_state") as mock_state:
        mock_state.return_value = {"last_sync": "2026-04-10T00:00:00Z", "total_movies": 15000, "total_tv": 5000}
        response = client.get("/api/admin/sync/status")
        assert response.status_code == 200
        data = response.json()
        assert "last_sync" in data

def test_sync_status_requires_auth(client):
    app.dependency_overrides.pop(verify_firebase_token, None)
    response = client.get("/api/admin/sync/status")
    assert response.status_code == 401
