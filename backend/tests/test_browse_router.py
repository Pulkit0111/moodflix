from unittest.mock import AsyncMock
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.routers.browse import get_tmdb_service

@pytest.fixture
def mock_tmdb():
    service = AsyncMock()
    app.dependency_overrides[get_tmdb_service] = lambda: service
    yield service
    app.dependency_overrides.clear()

@pytest.fixture
def client():
    return TestClient(app)

def test_trending_is_public(client, mock_tmdb):
    mock_tmdb.get_trending.return_value = [{"id": 550, "title": "Fight Club", "overview": "...", "poster_path": "/fc.jpg"}]
    response = client.get("/api/trending")
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_top_rated(client, mock_tmdb):
    mock_tmdb.get_top_rated.return_value = [{"id": 680, "title": "Pulp Fiction", "overview": "...", "poster_path": "/pf.jpg"}]
    response = client.get("/api/top-rated?media_type=movie")
    assert response.status_code == 200

def test_genres(client, mock_tmdb):
    mock_tmdb.get_genres.return_value = [{"id": 28, "name": "Action"}, {"id": 18, "name": "Drama"}]
    response = client.get("/api/genres")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_browse_by_genre(client, mock_tmdb):
    mock_tmdb.discover.return_value = ([{"id": 550, "title": "Fight Club"}], 10)
    response = client.get("/api/browse?genre=18&media_type=movie&page=1")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "total_pages" in data
