import json
import logging
from openai import AsyncOpenAI
from app.services.user_service import UserService
from app.config import settings

logger = logging.getLogger(__name__)

TASTE_PROMPT = """Analyze this user's movie/TV watching history and generate a taste profile.

Watch history (with genres and mood tags):
{history}

Return a JSON object with:
- "top_moods": array of {{"mood": string, "percentage": number}} (top 5 moods, percentages summing to 100)
- "genre_breakdown": array of {{"genre": string, "count": number}} (top 6 genres)
- "preferred_eras": array of {{"era": string, "count": number}} (e.g., "2020s", "2010s", "1990s")
- "director_affinities": array of up to 3 director name strings they seem to enjoy
- "summary": a 2-sentence personality-style description of their taste (be creative and fun)

Return ONLY the JSON object."""


class TasteService:
    def __init__(self, openai_client: AsyncOpenAI, user_service: UserService, collection):
        self.openai_client = openai_client
        self.user_service = user_service
        self.collection = collection

    async def analyze_taste(self, uid: str) -> dict | None:
        history = self.user_service.get_history(uid)
        if len(history) < 5:
            return None

        enriched = []
        for item in history:
            doc_id = f"{item.get('media_type', 'movie')}_{item['tmdb_id']}"
            meta_info = ""
            try:
                result = self.collection.get(ids=[doc_id], include=["metadatas"])
                if result["ids"]:
                    m = result["metadatas"][0]
                    meta_info = f"Genres: {m.get('genres', '')}. Moods: {m.get('mood_tags', '')}. Year: {m.get('release_year', 'N/A')}."
            except Exception:
                pass
            rating_str = f" (rated {item['rating']}/10)" if item.get("rating") else ""
            enriched.append(f"- {item['title']}{rating_str}. {meta_info}")

        history_text = "\n".join(enriched[-30:])

        try:
            response = await self.openai_client.chat.completions.create(
                model=settings.rerank_model,
                messages=[{"role": "user", "content": TASTE_PROMPT.format(history=history_text)}],
                temperature=0.5,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            logger.error("Taste analysis failed: %s", e)
            return None
