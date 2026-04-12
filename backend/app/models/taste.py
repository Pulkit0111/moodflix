from pydantic import BaseModel


class TasteDNA(BaseModel):
    top_moods: list[dict]
    genre_breakdown: list[dict]
    preferred_eras: list[dict]
    director_affinities: list[str]
    summary: str
