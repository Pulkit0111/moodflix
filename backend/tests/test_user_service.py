from unittest.mock import MagicMock
import pytest
from app.services.user_service import UserService

@pytest.fixture
def mock_db():
    return MagicMock()

@pytest.fixture
def user_service(mock_db):
    return UserService(db=mock_db)

def test_get_or_create_profile_existing(user_service, mock_db):
    doc_ref = MagicMock()
    doc_snapshot = MagicMock()
    doc_snapshot.exists = True
    doc_snapshot.to_dict.return_value = {"name": "Test User", "email": "test@example.com", "avatar_url": None, "created_at": "2026-01-01T00:00:00Z"}
    doc_ref.get.return_value = doc_snapshot
    mock_db.collection.return_value.document.return_value = doc_ref
    profile = user_service.get_or_create_profile("uid123", "Test User", "test@example.com", None)
    assert profile["name"] == "Test User"

def test_get_or_create_profile_new(user_service, mock_db):
    doc_ref = MagicMock()
    doc_snapshot = MagicMock()
    doc_snapshot.exists = False
    doc_ref.get.return_value = doc_snapshot
    mock_db.collection.return_value.document.return_value = doc_ref
    profile = user_service.get_or_create_profile("uid123", "New User", "new@example.com", None)
    doc_ref.set.assert_called_once()
    assert profile["name"] == "New User"

def test_get_watchlist(user_service, mock_db):
    mock_docs = [MagicMock(to_dict=MagicMock(return_value={"tmdb_id": 550, "media_type": "movie", "title": "Fight Club", "poster_path": "/fc.jpg", "added_at": "2026-01-01"}))]
    mock_db.collection.return_value.document.return_value.collection.return_value.order_by.return_value.stream.return_value = mock_docs
    watchlist = user_service.get_watchlist("uid123")
    assert len(watchlist) == 1
    assert watchlist[0]["title"] == "Fight Club"

def test_add_to_watchlist(user_service, mock_db):
    doc_ref = MagicMock()
    mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value = doc_ref
    user_service.add_to_watchlist("uid123", 550, "movie", "Fight Club", "/fc.jpg")
    doc_ref.set.assert_called_once()

def test_remove_from_watchlist(user_service, mock_db):
    doc_ref = MagicMock()
    mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value = doc_ref
    user_service.remove_from_watchlist("uid123", 550)
    doc_ref.delete.assert_called_once()

def test_add_to_history(user_service, mock_db):
    doc_ref = MagicMock()
    mock_db.collection.return_value.document.return_value.collection.return_value.document.return_value = doc_ref
    user_service.add_to_history("uid123", 550, "movie", "Fight Club", rating=4.5)
    doc_ref.set.assert_called_once()

def test_get_preferences(user_service, mock_db):
    doc_ref = MagicMock()
    doc_snapshot = MagicMock()
    doc_snapshot.exists = True
    doc_snapshot.to_dict.return_value = {"favorite_genres": ["Action", "Sci-Fi"], "disliked_genres": [], "preferred_decades": ["1990s"]}
    doc_ref.get.return_value = doc_snapshot
    mock_db.collection.return_value.document.return_value = doc_ref
    prefs = user_service.get_preferences("uid123")
    assert prefs["favorite_genres"] == ["Action", "Sci-Fi"]

def test_update_preferences(user_service, mock_db):
    doc_ref = MagicMock()
    mock_db.collection.return_value.document.return_value = doc_ref
    user_service.update_preferences("uid123", favorite_genres=["Drama"], disliked_genres=[], preferred_decades=[])
    doc_ref.set.assert_called_once()
