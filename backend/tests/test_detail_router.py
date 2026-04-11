from unittest.mock import AsyncMock, patch
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.routers.detail import get_tmdb_service

@pytest.fixture
def mock_tmdb():
    service = AsyncMock()
    app.dependency_overrides[get_tmdb_service] = lambda: service
    yield service
    app.dependency_overrides.clear()

@pytest.fixture
def client():
    return TestClient(app)

def test_get_title_details(client, mock_tmdb):
    mock_detail = {
        "id": 550, "title": "Fight Club", "overview": "An insomniac...",
        "release_date": "1999-10-15", "genres": [{"id": 18, "name": "Drama"}],
        "vote_average": 8.4, "popularity": 60.0, "poster_path": "/fc.jpg",
        "backdrop_path": "/fc_bg.jpg", "runtime": 139,
        "credits": {"cast": [{"name": "Brad Pitt", "character": "Tyler Durden", "profile_path": "/bp.jpg"}]},
        "videos": {"results": [{"key": "abc", "site": "YouTube", "type": "Trailer"}]},
        "watch/providers": {"results": {"US": {"flatrate": [{"provider_name": "Netflix"}]}}},
    }
    mock_tmdb.get_details.return_value = mock_detail
    response = client.get("/api/title/movie/550")
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Fight Club"
    assert data["runtime"] == 139

def test_get_similar_titles(client):
    with patch("app.routers.detail.get_similar_from_chroma") as mock_similar:
        mock_similar.return_value = [
            {"tmdb_id": 680, "media_type": "movie", "title": "Pulp Fiction", "poster_path": "/pf.jpg", "vote_average": 8.5}
        ]
        response = client.get("/api/title/movie/550/similar")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
