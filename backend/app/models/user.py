from pydantic import BaseModel

class UserProfile(BaseModel):
    uid: str
    name: str | None = None
    email: str | None = None
    avatar_url: str | None = None

class UserPreferences(BaseModel):
    favorite_genres: list[str] = []
    disliked_genres: list[str] = []
    preferred_decades: list[str] = []

class WatchlistItem(BaseModel):
    tmdb_id: int
    media_type: str
    title: str
    poster_path: str | None = None
    added_at: str | None = None

class HistoryItem(BaseModel):
    tmdb_id: int
    media_type: str
    title: str
    poster_path: str | None = None
    watched_at: str | None = None
    rating: float | None = None

class WatchlistAdd(BaseModel):
    tmdb_id: int
    media_type: str
    title: str
    poster_path: str | None = None

class HistoryAdd(BaseModel):
    tmdb_id: int
    media_type: str
    title: str
    poster_path: str | None = None
    rating: float | None = None
