import tempfile
import pytest
from app.dependencies import get_chroma_collection

def test_get_chroma_collection_creates_collection():
    with tempfile.TemporaryDirectory() as tmpdir:
        collection = get_chroma_collection(persist_dir=tmpdir)
        assert collection.name == "movies_tv"
        assert collection.count() == 0

def test_chroma_collection_can_add_and_query():
    with tempfile.TemporaryDirectory() as tmpdir:
        collection = get_chroma_collection(persist_dir=tmpdir)
        collection.add(
            ids=["movie_550"],
            documents=["Fight Club. An insomniac office worker..."],
            embeddings=[[0.1] * 1536],
            metadatas=[{
                "tmdb_id": 550, "media_type": "movie", "title": "Fight Club",
                "release_year": 1999, "genres": "Drama", "vote_average": 8.4,
                "popularity": 60.0, "poster_path": "/poster.jpg",
            }],
        )
        assert collection.count() == 1
        results = collection.query(query_embeddings=[[0.1] * 1536], n_results=1)
        assert results["ids"][0][0] == "movie_550"
