import json
import logging
from collections.abc import AsyncGenerator
from openai import AsyncOpenAI
from app.services.search_service import SearchService
from app.config import settings

logger = logging.getLogger(__name__)

CHAT_SYSTEM_PROMPT = """You are MoodFlix's AI matchmaker -- a friendly, knowledgeable movie guide. Your job is to help users discover movies and TV shows by understanding their mood, preferences, and context.

Rules:
1. Ask 1-2 clarifying questions to understand what the user wants (mood, genre, who they're watching with, etc.)
2. Keep responses concise and conversational
3. When you have enough context (usually after 1-2 exchanges), recommend 3-5 titles
4. For each recommendation, include a personalized one-sentence pitch
5. When recommending, include a JSON block with the recommendations:

```json
[{{"tmdb_id": 123, "title": "Movie Name", "media_type": "movie", "pitch": "One sentence pitch"}}]
```

6. After the JSON block, add a brief conversational follow-up

{user_context}"""


class ChatService:
    def __init__(self, search_service: SearchService, openai_client: AsyncOpenAI):
        self.search_service = search_service
        self.openai_client = openai_client

    def _extract_user_intent(self, messages: list[dict]) -> str:
        user_messages = [m["content"] for m in messages if m["role"] == "user"]
        return " ".join(user_messages[-3:])

    async def stream_chat(self, messages: list[dict], user_context: str = "") -> AsyncGenerator[str, None]:
        system_content = CHAT_SYSTEM_PROMPT.format(
            user_context=f"\nUser context: {user_context}" if user_context else ""
        )

        # If this looks like it needs recommendations (3+ messages), inject candidates
        api_messages = [{"role": "system", "content": system_content}]

        if len(messages) >= 3:
            intent = self._extract_user_intent(messages)
            try:
                candidates = await self.search_service.retrieve_candidates(intent, n=20)
                if candidates:
                    candidates_info = "\n".join(
                        f"- tmdb_id={c['tmdb_id']}, media_type={c['media_type']}, "
                        f"title=\"{c['title']}\" ({c.get('release_year', 'N/A')}), "
                        f"genres={c.get('genres', '')}, mood={','.join(c.get('mood_tags', []))}"
                        for c in candidates[:15]
                    )
                    api_messages[0]["content"] += (
                        f"\n\nAvailable titles to recommend from (use tmdb_id from this list):\n{candidates_info}"
                    )
            except Exception as e:
                logger.warning("Failed to fetch candidates for chat: %s", e)

        for msg in messages:
            api_messages.append({"role": msg["role"], "content": msg["content"]})

        stream = await self.openai_client.chat.completions.create(
            model=settings.chat_model,
            messages=api_messages,
            temperature=0.7,
            stream=True,
        )

        async for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
