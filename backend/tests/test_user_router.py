from unittest.mock import MagicMock
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import verify_firebase_token
from app.routers.user import get_user_service

MOCK_USER = {"uid": "user123", "name": "Test User", "email": "test@example.com", "picture": None}

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def mock_user_service():
    svc = MagicMock()
    svc.get_or_create_profile.return_value = {
        "uid": "user123", "name": "Test User", "email": "test@example.com", "avatar_url": None
    }
    svc.get_watchlist.return_value = [
        {"tmdb_id": 550, "media_type": "movie", "title": "Fight Club", "poster_path": "/fc.jpg", "added_at": "2024-01-01T00:00:00+00:00"}
    ]
    svc.add_to_watchlist.return_value = None
    svc.remove_from_watchlist.return_value = None
    svc.get_history.return_value = [
        {"tmdb_id": 550, "media_type": "movie", "title": "Fight Club", "watched_at": "2024-01-02T00:00:00+00:00", "rating": 9.0}
    ]
    svc.add_to_history.return_value = None
    svc.get_preferences.return_value = {
        "favorite_genres": ["Action"], "disliked_genres": [], "preferred_decades": ["1990s"]
    }
    svc.update_preferences.return_value = None
    svc.get_search_history.return_value = [
        {"query": "dark comedy", "searched_at": "2024-01-03T00:00:00+00:00"}
    ]
    return svc

@pytest.fixture(autouse=True)
def override_deps(mock_user_service):
    app.dependency_overrides[verify_firebase_token] = lambda: MOCK_USER
    app.dependency_overrides[get_user_service] = lambda: mock_user_service
    yield
    app.dependency_overrides.clear()


def test_get_profile(client, mock_user_service):
    response = client.get("/api/user/profile", headers={"Authorization": "Bearer fake-token"})
    assert response.status_code == 200
    data = response.json()
    assert data["uid"] == "user123"
    assert data["name"] == "Test User"
    mock_user_service.get_or_create_profile.assert_called_once_with(
        uid="user123", name="Test User", email="test@example.com", avatar_url=None
    )


def test_get_watchlist(client, mock_user_service):
    response = client.get("/api/user/watchlist", headers={"Authorization": "Bearer fake-token"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["tmdb_id"] == 550
    mock_user_service.get_watchlist.assert_called_once_with("user123")


def test_add_to_watchlist(client, mock_user_service):
    payload = {"tmdb_id": 550, "media_type": "movie", "title": "Fight Club", "poster_path": "/fc.jpg"}
    response = client.post("/api/user/watchlist", json=payload, headers={"Authorization": "Bearer fake-token"})
    assert response.status_code == 200
    assert response.json() == {"status": "added"}
    mock_user_service.add_to_watchlist.assert_called_once_with(
        uid="user123", tmdb_id=550, media_type="movie", title="Fight Club", poster_path="/fc.jpg"
    )


def test_delete_from_watchlist(client, mock_user_service):
    response = client.delete("/api/user/watchlist/550", headers={"Authorization": "Bearer fake-token"})
    assert response.status_code == 200
    assert response.json() == {"status": "removed"}
    mock_user_service.remove_from_watchlist.assert_called_once_with("user123", 550)


def test_get_history(client, mock_user_service):
    response = client.get("/api/user/history", headers={"Authorization": "Bearer fake-token"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["tmdb_id"] == 550
    mock_user_service.get_history.assert_called_once_with("user123")


def test_add_to_history(client, mock_user_service):
    payload = {"tmdb_id": 550, "media_type": "movie", "title": "Fight Club", "rating": 9.0}
    response = client.post("/api/user/history", json=payload, headers={"Authorization": "Bearer fake-token"})
    assert response.status_code == 200
    assert response.json() == {"status": "added"}
    mock_user_service.add_to_history.assert_called_once_with(
        uid="user123", tmdb_id=550, media_type="movie", title="Fight Club", rating=9.0
    )


def test_get_preferences(client, mock_user_service):
    response = client.get("/api/user/preferences", headers={"Authorization": "Bearer fake-token"})
    assert response.status_code == 200
    data = response.json()
    assert data["favorite_genres"] == ["Action"]
    assert data["preferred_decades"] == ["1990s"]
    mock_user_service.get_preferences.assert_called_once_with("user123")


def test_update_preferences(client, mock_user_service):
    payload = {"favorite_genres": ["Drama"], "disliked_genres": ["Horror"], "preferred_decades": ["2000s"]}
    response = client.put("/api/user/preferences", json=payload, headers={"Authorization": "Bearer fake-token"})
    assert response.status_code == 200
    assert response.json() == {"status": "updated"}
    mock_user_service.update_preferences.assert_called_once_with(
        uid="user123", favorite_genres=["Drama"], disliked_genres=["Horror"], preferred_decades=["2000s"]
    )


def test_get_search_history(client, mock_user_service):
    response = client.get("/api/user/search-history", headers={"Authorization": "Bearer fake-token"})
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["query"] == "dark comedy"
    mock_user_service.get_search_history.assert_called_once_with("user123")


def test_profile_requires_auth():
    app.dependency_overrides.clear()
    client = TestClient(app)
    response = client.get("/api/user/profile")
    assert response.status_code == 401
