import tempfile
import json
import os
import pytest
from app.workers.tmdb_sync import save_sync_state, load_sync_state
from app.workers.embedding_gen import build_embedding_text_from_tmdb

def test_save_and_load_sync_state():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "sync_state.json")
        state = {"last_sync": "2026-04-10", "total_movies": 100, "total_tv": 50}
        save_sync_state(state, path)
        loaded = load_sync_state(path)
        assert loaded["last_sync"] == "2026-04-10"
        assert loaded["total_movies"] == 100

def test_load_sync_state_missing_file():
    state = load_sync_state("/nonexistent/path.json")
    assert state["last_sync"] is None
    assert state["total_movies"] == 0

def test_build_embedding_text():
    movie = {"id": 550, "title": "Fight Club", "overview": "An insomniac office worker...", "genre_ids": [18, 53]}
    genre_map = {18: "Drama", 53: "Thriller"}
    text = build_embedding_text_from_tmdb(movie, genre_map, keywords=["dual identity", "underground"], cast=["Brad Pitt", "Edward Norton"])
    assert "Fight Club" in text
    assert "Drama" in text
    assert "dual identity" in text
    assert "Brad Pitt" in text
