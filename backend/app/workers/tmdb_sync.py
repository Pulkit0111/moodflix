import json
import os
import logging
import asyncio
from datetime import datetime, timezone
from app.config import settings
from app.services.tmdb_service import TMDBService

logger = logging.getLogger(__name__)

DEFAULT_STATE_PATH = os.path.normpath(os.path.join(settings.chroma_persist_dir, "..", "sync_state.json"))

def load_sync_state(path: str = DEFAULT_STATE_PATH) -> dict:
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {"last_sync": None, "total_movies": 0, "total_tv": 0, "page_cursor": 1}

def save_sync_state(state: dict, path: str = DEFAULT_STATE_PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(state, f, indent=2)

async def sync_popular(tmdb: TMDBService, media_type: str, max_pages: int = 50) -> list[dict]:
    all_items = []
    for page in range(1, max_pages + 1):
        try:
            items, total_pages = await tmdb.get_popular(media_type, page=page)
            all_items.extend(items)
            logger.info("Synced %s page %d/%d (%d items)", media_type, page, min(max_pages, total_pages), len(items))
            if page >= total_pages:
                break
        except Exception as e:
            logger.error("Error syncing %s page %d: %s", media_type, page, e)
            break
    return all_items

async def _run_sync():
    tmdb = TMDBService(api_key=settings.tmdb_api_key, base_url=settings.tmdb_base_url)
    state = load_sync_state()
    logger.info("Starting TMDB sync...")
    movies = await sync_popular(tmdb, "movie", max_pages=50)
    tv_shows = await sync_popular(tmdb, "tv", max_pages=50)
    state["last_sync"] = datetime.now(timezone.utc).isoformat()
    state["total_movies"] = len(movies)
    state["total_tv"] = len(tv_shows)
    save_sync_state(state)
    logger.info("TMDB sync complete: %d movies, %d TV shows", len(movies), len(tv_shows))
    from app.workers.embedding_gen import generate_embeddings
    await generate_embeddings(movies, tv_shows, tmdb)

def run_sync():
    asyncio.run(_run_sync())
