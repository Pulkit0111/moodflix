from unittest.mock import AsyncMock, MagicMock
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.dependencies import verify_firebase_token
from app.routers.search import get_search_service, get_user_service

@pytest.fixture
def client():
    return TestClient(app)

def test_search_requires_auth(client):
    response = client.post("/api/search", json={"query": "fun comedy"})
    assert response.status_code == 401

def test_search_returns_results(client):
    mock_user = {"uid": "user123", "name": "Test", "email": "test@example.com"}
    mock_results = [{"tmdb_id": 550, "media_type": "movie", "title": "Fight Club", "poster_path": "/fc.jpg", "vote_average": 8.4, "release_year": 1999, "match_reason": "Dark and intense drama"}]

    mock_service = AsyncMock()
    mock_service.search.return_value = mock_results

    mock_user_service = MagicMock()
    mock_user_service.get_preferences.return_value = {"favorite_genres": [], "disliked_genres": [], "preferred_decades": []}
    mock_user_service.get_history.return_value = []

    app.dependency_overrides[verify_firebase_token] = lambda: mock_user
    app.dependency_overrides[get_search_service] = lambda: mock_service
    app.dependency_overrides[get_user_service] = lambda: mock_user_service

    try:
        response = client.post("/api/search", json={"query": "dark intense drama"}, headers={"Authorization": "Bearer fake-token"})
        assert response.status_code == 200
        data = response.json()
        assert data["query"] == "dark intense drama"
        assert len(data["results"]) == 1
        assert data["results"][0]["title"] == "Fight Club"
    finally:
        app.dependency_overrides.clear()
