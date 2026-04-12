import logging
import time

from fastapi import APIRouter, HTTPException
from openai import AsyncOpenAI

from app.config import settings
from app.dependencies import get_chroma_collection
from app.services.embedding_service import EmbeddingService
from app.services.playlist_service import PlaylistService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["playlists"])

_playlist_cache: dict[str, dict] = {}
CACHE_TTL = 24 * 60 * 60  # 24 hours


def _get_playlist_service() -> PlaylistService:
    collection = get_chroma_collection()
    embedding_service = EmbeddingService(api_key=settings.openai_api_key, model=settings.embedding_model)
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    return PlaylistService(collection=collection, embedding_service=embedding_service, openai_client=client)


@router.get("/playlists")
async def get_playlists():
    service = _get_playlist_service()
    # Always return all playlists metadata
    return await service.get_all_playlists_metadata()


@router.get("/playlists/{mood_key}")
async def get_playlist(mood_key: str):
    cached = _playlist_cache.get(mood_key)
    if cached and (time.time() - cached.get("_cached_at", 0)) < CACHE_TTL:
        return cached

    service = _get_playlist_service()
    playlist = await service.generate_playlist(mood_key)
    if not playlist:
        raise HTTPException(status_code=404, detail="Playlist not found")

    playlist["_cached_at"] = time.time()
    _playlist_cache[mood_key] = playlist
    return playlist
