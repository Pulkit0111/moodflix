from pydantic import BaseModel
from app.models.media import MediaSummary

class SearchRequest(BaseModel):
    query: str
    filter_text: str | None = None

class SearchResult(MediaSummary):
    match_reason: str

class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
