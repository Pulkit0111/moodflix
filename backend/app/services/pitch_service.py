import json
import logging
from openai import AsyncOpenAI
from app.config import settings

logger = logging.getLogger(__name__)

PITCH_PROMPT = """You are a movie recommender. For each movie/show below, write ONE compelling sentence about why this specific user would love it. Be personal and specific -- reference their taste.

User's taste:
{user_context}

Movies to pitch:
{items}

Return a JSON object mapping tmdb_id to pitch string. Example: {{"123": "pitch text", "456": "pitch text"}}
Return ONLY the JSON object."""


class PitchService:
    def __init__(self, openai_client: AsyncOpenAI):
        self.openai_client = openai_client

    async def generate_pitch(self, title: str, overview: str, genres: str, user_context: str) -> str:
        try:
            response = await self.openai_client.chat.completions.create(
                model=settings.rerank_model,
                messages=[{"role": "user", "content": (
                    f"User's taste: {user_context}\n\n"
                    f"Movie: {title}. {overview[:200]}. Genres: {genres}.\n\n"
                    "Write ONE compelling sentence about why this user would love this. "
                    "Be personal and specific. Return ONLY the sentence."
                )}],
                temperature=0.5,
                max_tokens=100,
            )
            return response.choices[0].message.content.strip().strip('"')
        except Exception as e:
            logger.error("Pitch generation failed: %s", e)
            return ""

    async def generate_pitches_batch(self, items: list[dict], user_context: str) -> dict[str, str]:
        if not items or not user_context:
            return {}

        items_text = "\n".join(
            f"- [tmdb_id={it['tmdb_id']}] {it['title']}: {it.get('overview', '')[:100]}. Genres: {it.get('genres', '')}"
            for it in items
        )

        try:
            response = await self.openai_client.chat.completions.create(
                model=settings.rerank_model,
                messages=[{"role": "user", "content": PITCH_PROMPT.format(
                    user_context=user_context, items=items_text
                )}],
                temperature=0.5,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content
            parsed = json.loads(content)
            return {str(k): v for k, v in parsed.items()} if isinstance(parsed, dict) else {}
        except Exception as e:
            logger.error("Batch pitch generation failed: %s", e)
            return {}
