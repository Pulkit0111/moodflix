import logging

from fastapi import APIRouter, Depends, Query
import httpx

from app.services.tmdb_service import TMDBService
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["browse"])

def get_tmdb_service() -> TMDBService:
    return TMDBService(api_key=settings.tmdb_api_key, base_url=settings.tmdb_base_url)

@router.get("/trending")
async def trending(page: int = Query(default=1, ge=1), tmdb: TMDBService = Depends(get_tmdb_service)):
    try:
        return await tmdb.get_trending(page=page)
    except (httpx.HTTPStatusError, httpx.ConnectError) as e:
        logger.error("TMDB API error on /trending: %s", e)
        return []

@router.get("/top-rated")
async def top_rated(media_type: str = Query(default="movie", pattern="^(movie|tv)$"), page: int = Query(default=1, ge=1), tmdb: TMDBService = Depends(get_tmdb_service)):
    try:
        return await tmdb.get_top_rated(media_type=media_type, page=page)
    except (httpx.HTTPStatusError, httpx.ConnectError) as e:
        logger.error("TMDB API error on /top-rated: %s", e)
        return []

@router.get("/genres")
async def genres(media_type: str = Query(default="movie", pattern="^(movie|tv)$"), tmdb: TMDBService = Depends(get_tmdb_service)):
    try:
        return await tmdb.get_genres(media_type=media_type)
    except (httpx.HTTPStatusError, httpx.ConnectError) as e:
        logger.error("TMDB API error on /genres: %s", e)
        return []

@router.get("/browse")
async def browse(genre: int = Query(...), media_type: str = Query(default="movie", pattern="^(movie|tv)$"), page: int = Query(default=1, ge=1), tmdb: TMDBService = Depends(get_tmdb_service)):
    try:
        results, total_pages = await tmdb.discover(media_type=media_type, genre_id=genre, page=page)
        return {"results": results, "total_pages": total_pages}
    except (httpx.HTTPStatusError, httpx.ConnectError) as e:
        logger.error("TMDB API error on /browse: %s", e)
        return {"results": [], "total_pages": 0}
