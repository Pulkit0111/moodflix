import json
import logging
from openai import AsyncOpenAI
from app.config import settings
from app.services.tmdb_service import TMDBService
from app.services.embedding_service import EmbeddingService
from app.dependencies import get_chroma_collection

logger = logging.getLogger(__name__)
BATCH_SIZE = 100

MOOD_VOCABULARY = [
    "heartwarming", "slow-burn", "mind-bending", "adrenaline-rush", "cozy",
    "dark", "nostalgic", "feel-good", "romantic", "epic", "thrilling",
    "cerebral", "bittersweet", "whimsical", "intense", "melancholic",
    "uplifting", "suspenseful", "quirky", "emotional",
]

MOOD_CLASSIFY_PROMPT = """Classify each movie/show with 3-5 mood tags from this vocabulary:
{vocabulary}

For each item, return ONLY tags from the vocabulary above.

Items:
{items}

Return a JSON array where each element has "id" and "tags" (list of strings). Example:
[{{"id": "movie_123", "tags": ["dark", "intense", "suspenseful"]}}]

Return ONLY the JSON array."""


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


async def classify_mood_tags_batch(items: list[dict], client: AsyncOpenAI) -> dict[str, list[str]]:
    items_text = "\n".join(
        f"- [{it['id']}] {it['title']}: {it.get('overview', '')[:150]}"
        for it in items
    )
    try:
        response = await client.chat.completions.create(
            model=settings.mood_classification_model,
            messages=[{"role": "user", "content": MOOD_CLASSIFY_PROMPT.format(
                vocabulary=", ".join(MOOD_VOCABULARY), items=items_text
            )}],
            temperature=0.2,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        parsed = json.loads(content)
        if isinstance(parsed, dict):
            parsed = parsed.get("results", parsed.get("items", []))
        result = {}
        for entry in parsed:
            doc_id = entry.get("id", "")
            tags = [t for t in entry.get("tags", []) if t in MOOD_VOCABULARY]
            if doc_id and tags:
                result[doc_id] = tags
        return result
    except Exception as e:
        logger.error("Mood classification failed: %s", e)
        return {}


async def backfill_mood_tags():
    collection = get_chroma_collection()
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    count = collection.count()
    if count == 0:
        logger.info("No items in ChromaDB to backfill")
        return

    logger.info("Backfilling mood tags for %d items", count)
    all_data = collection.get(include=["metadatas", "documents"], limit=count)

    items_without_tags = []
    for i, doc_id in enumerate(all_data["ids"]):
        meta = all_data["metadatas"][i]
        if not meta.get("mood_tags"):
            items_without_tags.append({
                "id": doc_id,
                "title": meta.get("title", ""),
                "overview": (all_data["documents"][i] or "")[:200],
            })

    logger.info("Found %d items without mood tags", len(items_without_tags))

    for i in range(0, len(items_without_tags), 10):
        batch = items_without_tags[i:i + 10]
        tags_map = await classify_mood_tags_batch(batch, client)

        for item in batch:
            doc_id = item["id"]
            tags = tags_map.get(doc_id, [])
            if tags:
                idx = all_data["ids"].index(doc_id)
                meta = all_data["metadatas"][idx]
                meta["mood_tags"] = ",".join(tags)
                collection.update(ids=[doc_id], metadatas=[meta])

        classified = sum(1 for item in batch if item["id"] in tags_map)
        logger.info("Backfilled batch %d-%d (%d/%d classified)", i, i + len(batch), classified, len(batch))

    logger.info("Mood tag backfill complete")


async def generate_embeddings(movies: list[dict], tv_shows: list[dict], tmdb: TMDBService):
    embedding_service = EmbeddingService(api_key=settings.openai_api_key, model=settings.embedding_model)
    client = AsyncOpenAI(api_key=settings.openai_api_key)
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
        classify_inputs = []
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
                "mood_tags": "",
            })
            classify_inputs.append({
                "id": doc_id, "title": title,
                "overview": item.get("overview", "")[:200],
            })

        # Classify mood tags in sub-batches of 10
        for ci in range(0, len(classify_inputs), 10):
            sub = classify_inputs[ci:ci + 10]
            tags_map = await classify_mood_tags_batch(sub, client)
            for entry in sub:
                tags = tags_map.get(entry["id"], [])
                idx = ids.index(entry["id"])
                metadatas[idx]["mood_tags"] = ",".join(tags)

        try:
            embeddings = await embedding_service.embed_batch(texts)
            collection.upsert(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)
            logger.info("Embedded batch %d-%d (%d items)", i, i+len(batch), len(batch))
        except Exception as e:
            logger.error("Error embedding batch %d: %s", i, e)

    logger.info("Embedding generation complete. Collection size: %d", collection.count())
