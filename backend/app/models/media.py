from pydantic import BaseModel

class MediaItem(BaseModel):
    tmdb_id: int
    media_type: str  # "movie" or "tv"
    title: str
    overview: str
    release_year: int | None = None
    genres: list[str] = []
    vote_average: float = 0.0
    popularity: float = 0.0
    poster_path: str | None = None
    backdrop_path: str | None = None

class MediaDetail(MediaItem):
    runtime: int | None = None
    cast: list[dict] = []
    videos: list[dict] = []
    watch_providers: dict = {}

class MediaSummary(BaseModel):
    tmdb_id: int
    media_type: str
    title: str
    poster_path: str | None = None
    vote_average: float = 0.0
    release_year: int | None = None
    mood_tags: list[str] = []
