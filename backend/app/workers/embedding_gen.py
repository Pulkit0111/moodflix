import logging
from app.config import settings
from app.services.tmdb_service import TMDBService
from app.services.embedding_service import EmbeddingService
from app.dependencies import get_chroma_collection

logger = logging.getLogger(__name__)
BATCH_SIZE = 100

def build_embedding_text_from_tmdb(item: dict, genre_map: dict[int, str], keywords: list[str], cast: list[str]) -> str:
    title = item.get("title") or item.get("name", "Unknown")
    overview = item.get("overview", "")
    genre_names = [genre_map.get(gid, "") for gid in item.get("genre_ids", [])]
    genre_names = [g for g in genre_names if g]
    parts = [f"{title}. {overview}"]
    if genre_names:
        parts.append(f"Genres: {', '.join(genre_names)}.")
    if keywords:
        parts.append(f"Keywords: {', '.join(keywords)}.")
    if cast:
        parts.append(f"Cast: {', '.join(cast)}.")
    return " ".join(parts)

def _extract_year(item: dict) -> int | None:
    date_str = item.get("release_date") or item.get("first_air_date") or ""
    if date_str and len(date_str) >= 4:
        try:
            return int(date_str[:4])
        except ValueError:
            return None
    return None

async def generate_embeddings(movies: list[dict], tv_shows: list[dict], tmdb: TMDBService):
    embedding_service = EmbeddingService(api_key=settings.openai_api_key, model=settings.embedding_model)
    collection = get_chroma_collection()
    movie_genres_list = await tmdb.get_genres("movie")
    tv_genres_list = await tmdb.get_genres("tv")
    genre_map = {}
    for g in movie_genres_list + tv_genres_list:
        genre_map[g["id"]] = g["name"]

    all_items = [("movie", item) for item in movies] + [("tv", item) for item in tv_shows]

    existing_ids = set()
    try:
        all_possible_ids = [f"{mt}_{item['id']}" for mt, item in all_items]
        for i in range(0, len(all_possible_ids), 1000):
            batch_ids = all_possible_ids[i:i+1000]
            result = collection.get(ids=batch_ids)
            existing_ids.update(result["ids"])
    except Exception:
        pass

    new_items = [(mt, item) for mt, item in all_items if f"{mt}_{item['id']}" not in existing_ids]
    logger.info("Generating embeddings for %d new items (skipping %d existing)", len(new_items), len(existing_ids))

    for i in range(0, len(new_items), BATCH_SIZE):
        batch = new_items[i:i+BATCH_SIZE]
        texts, ids, metadatas = [], [], []
        seen_in_batch = set()
        for media_type, item in batch:
            doc_id = f"{media_type}_{item['id']}"
            if doc_id in seen_in_batch:
                continue
            seen_in_batch.add(doc_id)
            title = item.get("title") or item.get("name", "Unknown")
            text = build_embedding_text_from_tmdb(item, genre_map, keywords=[], cast=[])
            texts.append(text)
            ids.append(doc_id)
            genre_names = [genre_map.get(gid, "") for gid in item.get("genre_ids", [])]
            genre_names = [g for g in genre_names if g]
            metadatas.append({
                "tmdb_id": item["id"], "media_type": media_type, "title": title,
                "release_year": _extract_year(item) or 0, "genres": ",".join(genre_names),
                "vote_average": item.get("vote_average", 0), "popularity": item.get("popularity", 0),
                "poster_path": item.get("poster_path") or "",
            })
        try:
            embeddings = await embedding_service.embed_batch(texts)
            collection.upsert(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)
            logger.info("Embedded batch %d-%d (%d items)", i, i+len(batch), len(batch))
        except Exception as e:
            logger.error("Error embedding batch %d: %s", i, e)

    logger.info("Embedding generation complete. Collection size: %d", collection.count())
