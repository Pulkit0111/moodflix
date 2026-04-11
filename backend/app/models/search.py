from pydantic import BaseModel
from app.models.media import MediaSummary

class SearchRequest(BaseModel):
    query: str

class SearchResult(MediaSummary):
    match_reason: str

class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
