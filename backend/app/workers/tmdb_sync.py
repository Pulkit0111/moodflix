import json
import os
import logging
import asyncio
from datetime import datetime, timezone
from app.config import settings
from app.services.tmdb_service import TMDBService

logger = logging.getLogger(__name__)

DEFAULT_STATE_PATH = os.path.normpath(os.path.join(settings.chroma_persist_dir, "..", "sync_state.json"))

# Languages to sync for regional cinema coverage
REGIONAL_LANGUAGES = [
    ("hi", "Hindi / Bollywood"),
    ("ko", "Korean"),
    ("ja", "Japanese"),
    ("fr", "French"),
    ("es", "Spanish"),
    ("de", "German"),
    ("it", "Italian"),
    ("ta", "Tamil"),
    ("te", "Telugu"),
    ("ml", "Malayalam"),
    ("zh", "Chinese"),
    ("pt", "Portuguese"),
    ("tr", "Turkish"),
    ("th", "Thai"),
]


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
            if page % 20 == 0:
                logger.info("Synced %s popular page %d/%d (%d items total)", media_type, page, min(max_pages, total_pages), len(all_items))
            if page >= total_pages:
                break
        except Exception as e:
            logger.error("Error syncing %s popular page %d: %s", media_type, page, e)
            break
    return all_items


async def sync_top_rated(tmdb: TMDBService, media_type: str, max_pages: int = 30) -> list[dict]:
    all_items = []
    for page in range(1, max_pages + 1):
        try:
            items = await tmdb.get_top_rated(media_type, page=page)
            all_items.extend(items)
            if page >= 30:
                break
        except Exception as e:
            logger.error("Error syncing %s top_rated page %d: %s", media_type, page, e)
            break
    logger.info("Synced %s top_rated: %d items", media_type, len(all_items))
    return all_items


async def sync_regional(tmdb: TMDBService, media_type: str, lang_code: str, lang_name: str, max_pages: int = 15) -> list[dict]:
    all_items = []
    for page in range(1, max_pages + 1):
        try:
            items, total_pages = await tmdb.discover(media_type, page=page, original_language=lang_code)
            all_items.extend(items)
            if page >= total_pages:
                break
        except Exception as e:
            logger.error("Error syncing %s %s page %d: %s", media_type, lang_name, page, e)
            break
    if all_items:
        logger.info("Synced %s %s: %d items", media_type, lang_name, len(all_items))
    return all_items


def deduplicate(items: list[dict]) -> list[dict]:
    seen = set()
    unique = []
    for item in items:
        item_id = item.get("id")
        if item_id and item_id not in seen:
            seen.add(item_id)
            unique.append(item)
    return unique


async def _run_sync():
    tmdb = TMDBService(api_key=settings.tmdb_api_key, base_url=settings.tmdb_base_url)
    state = load_sync_state()
    logger.info("Starting expanded TMDB sync...")

    movies = []
    tv_shows = []

    # 1. Popular (100 pages each = ~2000 items each)
    logger.info("--- Syncing popular content ---")
    movies.extend(await sync_popular(tmdb, "movie", max_pages=100))
    tv_shows.extend(await sync_popular(tmdb, "tv", max_pages=100))

    # 2. Top rated (30 pages each = ~600 items each)
    logger.info("--- Syncing top rated content ---")
    movies.extend(await sync_top_rated(tmdb, "movie", max_pages=30))
    tv_shows.extend(await sync_top_rated(tmdb, "tv", max_pages=30))

    # 3. Regional cinema (15 pages per language per type)
    logger.info("--- Syncing regional cinema ---")
    for lang_code, lang_name in REGIONAL_LANGUAGES:
        movies.extend(await sync_regional(tmdb, "movie", lang_code, lang_name, max_pages=15))
        tv_shows.extend(await sync_regional(tmdb, "tv", lang_code, lang_name, max_pages=10))

    # Deduplicate
    movies = deduplicate(movies)
    tv_shows = deduplicate(tv_shows)

    state["last_sync"] = datetime.now(timezone.utc).isoformat()
    state["total_movies"] = len(movies)
    state["total_tv"] = len(tv_shows)
    save_sync_state(state)
    logger.info("TMDB sync complete: %d unique movies, %d unique TV shows", len(movies), len(tv_shows))

    from app.workers.embedding_gen import generate_embeddings
    await generate_embeddings(movies, tv_shows, tmdb)


def run_sync():
    asyncio.run(_run_sync())
