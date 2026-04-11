import pytest
from app.services.tmdb_service import TMDBService

@pytest.fixture
def tmdb_service():
    return TMDBService(api_key="fake-key", base_url="https://api.themoviedb.org/3")

@pytest.fixture
def mock_movie_response():
    return {
        "results": [
            {
                "id": 550, "title": "Fight Club", "overview": "An insomniac office worker...",
                "release_date": "1999-10-15", "genre_ids": [18], "vote_average": 8.4,
                "popularity": 60.0, "poster_path": "/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg",
                "backdrop_path": "/hZkgoQYus5dXo3H8T7Uef6DNknx.jpg",
            }
        ],
        "page": 1, "total_pages": 10,
    }

@pytest.fixture
def mock_genre_response():
    return {"genres": [{"id": 28, "name": "Action"}, {"id": 18, "name": "Drama"}]}

@pytest.mark.asyncio
async def test_get_trending(tmdb_service, mock_movie_response, httpx_mock):
    httpx_mock.add_response(
        url="https://api.themoviedb.org/3/trending/all/week",
        match_params={"language": "en-US", "page": "1"},
        json=mock_movie_response,
    )
    results = await tmdb_service.get_trending()
    assert len(results) == 1
    assert results[0]["id"] == 550

@pytest.mark.asyncio
async def test_get_movie_genres(tmdb_service, mock_genre_response, httpx_mock):
    httpx_mock.add_response(
        url="https://api.themoviedb.org/3/genre/movie/list",
        match_params={"language": "en-US"},
        json=mock_genre_response,
    )
    genres = await tmdb_service.get_genres("movie")
    assert len(genres) == 2
    assert genres[0]["name"] == "Action"

@pytest.mark.asyncio
async def test_get_movie_details(tmdb_service, httpx_mock):
    httpx_mock.add_response(
        url="https://api.themoviedb.org/3/movie/550",
        match_params={"language": "en-US", "append_to_response": "credits,videos,watch/providers"},
        json={
            "id": 550, "title": "Fight Club", "overview": "An insomniac office worker...",
            "release_date": "1999-10-15", "genres": [{"id": 18, "name": "Drama"}],
            "vote_average": 8.4, "popularity": 60.0,
            "poster_path": "/pB8BM7pdSp6B6Ih7QZ4DrQ3PmJK.jpg",
            "backdrop_path": "/hZkgoQYus5dXo3H8T7Uef6DNknx.jpg",
            "runtime": 139,
            "credits": {"cast": [{"name": "Brad Pitt", "character": "Tyler Durden", "profile_path": "/path.jpg"}]},
            "videos": {"results": [{"key": "abc123", "site": "YouTube", "type": "Trailer"}]},
            "watch/providers": {"results": {"US": {"flatrate": [{"provider_name": "Netflix"}]}}},
        },
    )
    detail = await tmdb_service.get_details("movie", 550)
    assert detail["title"] == "Fight Club"
    assert detail["runtime"] == 139

@pytest.mark.asyncio
async def test_discover_movies(tmdb_service, mock_movie_response, httpx_mock):
    httpx_mock.add_response(
        url="https://api.themoviedb.org/3/discover/movie",
        match_params={"language": "en-US", "sort_by": "popularity.desc", "page": "1", "with_genres": "18"},
        json=mock_movie_response,
    )
    results, total_pages = await tmdb_service.discover("movie", genre_id=18, page=1)
    assert len(results) == 1
    assert total_pages == 10
