from unittest.mock import AsyncMock, MagicMock, patch
import pytest
from app.services.embedding_service import EmbeddingService


@pytest.fixture
def embedding_service():
    return EmbeddingService(api_key="fake-key", model="text-embedding-3-small")


@pytest.mark.asyncio
async def test_embed_single_text(embedding_service):
    mock_response = MagicMock()
    mock_response.data = [MagicMock(embedding=[0.1, 0.2, 0.3])]
    with patch.object(embedding_service.client.embeddings, "create", new_callable=AsyncMock, return_value=mock_response):
        result = await embedding_service.embed_text("a fun movie about space")
        assert result == [0.1, 0.2, 0.3]


@pytest.mark.asyncio
async def test_embed_batch(embedding_service):
    mock_response = MagicMock()
    mock_response.data = [MagicMock(embedding=[0.1, 0.2, 0.3]), MagicMock(embedding=[0.4, 0.5, 0.6])]
    with patch.object(embedding_service.client.embeddings, "create", new_callable=AsyncMock, return_value=mock_response):
        results = await embedding_service.embed_batch(["text one", "text two"])
        assert len(results) == 2
        assert results[0] == [0.1, 0.2, 0.3]
        assert results[1] == [0.4, 0.5, 0.6]


def test_build_movie_text(embedding_service):
    text = embedding_service.build_movie_text(
        title="Inception",
        overview="A thief who steals corporate secrets through dream-sharing technology.",
        genres=["Action", "Sci-Fi"],
        keywords=["dream", "heist"],
        cast=["Leonardo DiCaprio", "Tom Hardy"],
    )
    assert "Inception" in text
    assert "dream-sharing technology" in text
    assert "Action" in text
    assert "dream" in text
    assert "Leonardo DiCaprio" in text
