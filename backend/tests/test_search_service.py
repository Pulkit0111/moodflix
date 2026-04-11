import tempfile
import json
from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from app.services.search_service import SearchService
from app.services.embedding_service import EmbeddingService
from app.dependencies import get_chroma_collection

@pytest.fixture
def chroma_collection():
    with tempfile.TemporaryDirectory() as tmpdir:
        collection = get_chroma_collection(persist_dir=tmpdir)
        collection.add(
            ids=["movie_550", "movie_680", "tv_1399"],
            documents=[
                "Fight Club. An insomniac office worker and a devil-may-care soap maker form an underground fight club. Genres: Drama. Keywords: dual identity, underground. Cast: Brad Pitt, Edward Norton.",
                "Pulp Fiction. The lives of two mob hitmen intertwine. Genres: Crime, Drama. Keywords: nonlinear, crime. Cast: John Travolta, Uma Thurman.",
                "Breaking Bad. A chemistry teacher diagnosed with cancer turns to manufacturing meth. Genres: Drama, Crime. Keywords: transformation, drugs. Cast: Bryan Cranston, Aaron Paul.",
            ],
            embeddings=[[0.1] * 1536, [0.2] * 1536, [0.3] * 1536],
            metadatas=[
                {"tmdb_id": 550, "media_type": "movie", "title": "Fight Club", "release_year": 1999, "genres": "Drama", "vote_average": 8.4, "popularity": 60.0, "poster_path": "/fight.jpg"},
                {"tmdb_id": 680, "media_type": "movie", "title": "Pulp Fiction", "release_year": 1994, "genres": "Crime,Drama", "vote_average": 8.5, "popularity": 70.0, "poster_path": "/pulp.jpg"},
                {"tmdb_id": 1399, "media_type": "tv", "title": "Breaking Bad", "release_year": 2008, "genres": "Drama,Crime", "vote_average": 8.9, "popularity": 80.0, "poster_path": "/bb.jpg"},
            ],
        )
        yield collection

@pytest.fixture
def mock_embedding_service():
    service = AsyncMock(spec=EmbeddingService)
    service.embed_text = AsyncMock(return_value=[0.15] * 1536)
    return service

@pytest.fixture
def search_service(chroma_collection, mock_embedding_service):
    return SearchService(
        collection=chroma_collection, embedding_service=mock_embedding_service,
        rerank_model="gpt-4o-mini", openai_api_key="fake-key",
    )

@pytest.mark.asyncio
async def test_retrieve_candidates(search_service):
    candidates = await search_service.retrieve_candidates("dark gritty drama", n=3)
    assert len(candidates) == 3
    assert all("tmdb_id" in c for c in candidates)

@pytest.mark.asyncio
async def test_search_returns_results(search_service):
    mock_rerank_response = MagicMock()
    mock_rerank_response.choices = [
        MagicMock(message=MagicMock(content=json.dumps([
            {"tmdb_id": 550, "match_reason": "Dark and gritty drama about identity"},
            {"tmdb_id": 1399, "match_reason": "Intense dramatic transformation story"},
        ])))
    ]
    with patch.object(search_service.openai_client.chat.completions, "create", new_callable=AsyncMock, return_value=mock_rerank_response):
        results = await search_service.search("dark gritty drama")
        assert len(results) == 2
        assert results[0]["tmdb_id"] == 550
        assert "match_reason" in results[0]
