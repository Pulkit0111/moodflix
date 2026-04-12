import logging
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from openai import AsyncOpenAI

from app.config import settings
from app.dependencies import get_chroma_collection
from app.services.embedding_service import EmbeddingService
from app.services.playlist_service import PlaylistService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["playlists"])

# Simple in-memory cache (replaced by Firestore in production)
_playlist_cache: dict[str, dict] = {}
_cache_ts: float = 0
CACHE_TTL = 24 * 60 * 60  # 24 hours


def _get_playlist_service() -> PlaylistService:
    collection = get_chroma_collection()
    embedding_service = EmbeddingService(api_key=settings.openai_api_key, model=settings.embedding_model)
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    return PlaylistService(collection=collection, embedding_service=embedding_service, openai_client=client)


def _cache_valid() -> bool:
    import time
    return bool(_playlist_cache) and (time.time() - _cache_ts) < CACHE_TTL


@router.get("/playlists")
async def get_playlists():
    service = _get_playlist_service()
    if _cache_valid():
        return list(_playlist_cache.values())

    metadata = await service.get_all_playlists_metadata()
    return metadata


@router.get("/playlists/{mood_key}")
async def get_playlist(mood_key: str):
    import time
    global _playlist_cache, _cache_ts

    if mood_key in _playlist_cache and _cache_valid():
        return _playlist_cache[mood_key]

    service = _get_playlist_service()
    playlist = await service.generate_playlist(mood_key)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    _playlist_cache[mood_key] = playlist
    _cache_ts = time.time()
    return playlist
