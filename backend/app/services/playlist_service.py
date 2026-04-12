import json
import logging
from datetime import datetime, timezone
from openai import AsyncOpenAI
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

MOOD_DEFINITIONS = {
    "cozy-rainy-day": {"name": "Cozy Rainy Day", "description": "Warm, comforting films perfect for curling up indoors", "query": "cozy comforting warm heartwarming gentle slow"},
    "adrenaline-rush": {"name": "Adrenaline Rush", "description": "High-octane thrills that keep your heart racing", "query": "thrilling intense action adrenaline exciting fast-paced"},
    "post-breakup-comfort": {"name": "Post-Breakup Comfort", "description": "Stories of healing, self-discovery, and moving forward", "query": "healing moving on self-discovery empowering uplifting after heartbreak"},
    "mind-benders": {"name": "Mind Benders", "description": "Films that make you question everything you know", "query": "mind-bending cerebral twist philosophical thought-provoking puzzle"},
    "feel-good-friday": {"name": "Feel-Good Friday", "description": "Pure joy and laughter to end the week right", "query": "feel-good happy funny lighthearted joyful comedy"},
    "late-night-dark": {"name": "Late Night Dark", "description": "Dark, atmospheric stories best watched after midnight", "query": "dark atmospheric noir gritty moody intense psychological"},
    "nostalgic-rewind": {"name": "Nostalgic Rewind", "description": "Timeless classics that take you back", "query": "nostalgic classic retro timeless coming-of-age memorable"},
    "epic-adventures": {"name": "Epic Adventures", "description": "Grand journeys and sweeping tales of courage", "query": "epic adventure journey grand sweeping heroic ambitious"},
    "romantic-escape": {"name": "Romantic Escape", "description": "Love stories that make your heart flutter", "query": "romantic love sweet passionate tender beautiful relationship"},
    "quirky-gems": {"name": "Quirky Gems", "description": "Offbeat indie finds with a unique voice", "query": "quirky indie unique offbeat whimsical unconventional creative"},
}

PLAYLIST_SELECT_PROMPT = """You are a movie curator. Given these candidate movies/shows and a playlist theme, select the 12 best fits.

Playlist: {name}
Theme: {description}

Candidates:
{candidates}

Return a JSON array of the 12 best matches. Each entry: {{"tmdb_id": int, "reason": "one sentence why it fits this playlist"}}
Return ONLY the JSON array."""


class PlaylistService:
    def __init__(self, collection, embedding_service: EmbeddingService, openai_client: AsyncOpenAI):
        self.collection = collection
        self.embedding_service = embedding_service
        self.openai_client = openai_client

    async def generate_playlist(self, mood_key: str) -> dict | None:
        mood = MOOD_DEFINITIONS.get(mood_key)
        if not mood:
            return None

        query_embedding = await self.embedding_service.embed_text(mood["query"])
        count = self.collection.count()
        if count == 0:
            return None

        results = self.collection.query(query_embeddings=[query_embedding], n_results=min(30, count))
        if not results["ids"] or not results["ids"][0]:
            return None

        candidates_text = "\n".join(
            f"- [tmdb_id={results['metadatas'][0][i]['tmdb_id']}] {results['metadatas'][0][i]['title']} "
            f"({results['metadatas'][0][i].get('release_year', 'N/A')}): "
            f"{(results['documents'][0][i] or '')[:150]}"
            for i in range(len(results["ids"][0]))
        )

        try:
            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": PLAYLIST_SELECT_PROMPT.format(
                    name=mood["name"], description=mood["description"], candidates=candidates_text
                )}],
                temperature=0.3,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
            if isinstance(parsed, dict):
                parsed = parsed.get("results", parsed.get("matches", parsed.get("items", [])))
        except Exception as e:
            logger.error("Playlist generation failed for %s: %s", mood_key, e)
            return None

        meta_by_id = {}
        for i, doc_id in enumerate(results["ids"][0]):
            m = results["metadatas"][0][i]
            meta_by_id[m["tmdb_id"]] = m

        items = []
        for entry in parsed[:15]:
            tmdb_id = entry.get("tmdb_id")
            if tmdb_id in meta_by_id:
                m = meta_by_id[tmdb_id]
                tags_str = m.get("mood_tags", "")
                items.append({
                    "tmdb_id": tmdb_id,
                    "media_type": m["media_type"],
                    "title": m["title"],
                    "poster_path": m.get("poster_path") or None,
                    "vote_average": m.get("vote_average", 0),
                    "release_year": m.get("release_year"),
                    "mood_tags": [t.strip() for t in tags_str.split(",") if t.strip()] if tags_str else [],
                })

        return {
            "id": mood_key,
            "name": mood["name"],
            "description": mood["description"],
            "mood_key": mood_key,
            "items": items,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }

    async def get_all_playlists_metadata(self) -> list[dict]:
        return [
            {"id": key, "name": mood["name"], "description": mood["description"], "mood_key": key}
            for key, mood in MOOD_DEFINITIONS.items()
        ]
