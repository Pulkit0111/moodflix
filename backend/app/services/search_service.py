import json
import logging
from chromadb.api.models.Collection import Collection
from openai import AsyncOpenAI
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

RERANK_SYSTEM_PROMPT = """You are a movie recommendation expert. Given a user's mood/description and a list of candidate movies/shows, rank the best matches.

Return a JSON array of the top {result_count} matches. Each entry must have:
- "tmdb_id": int
- "match_reason": string (one sentence explaining why this matches the user's mood)

Return ONLY the JSON array, no other text."""

RERANK_USER_PROMPT = """User's mood/request: "{query}"

{personalization}

Candidates:
{candidates}

Return the top {result_count} matches as a JSON array."""


class SearchService:
    def __init__(self, collection: Collection, embedding_service: EmbeddingService, rerank_model: str, openai_api_key: str, candidate_count: int = 50, result_count: int = 10):
        self.collection = collection
        self.embedding_service = embedding_service
        self.rerank_model = rerank_model
        self.openai_client = AsyncOpenAI(api_key=openai_api_key)
        self.candidate_count = candidate_count
        self.result_count = result_count

    async def retrieve_candidates(self, query: str, n: int | None = None) -> list[dict]:
        n = n or self.candidate_count
        query_embedding = await self.embedding_service.embed_text(query)
        results = self.collection.query(query_embeddings=[query_embedding], n_results=min(n, self.collection.count()))
        candidates = []
        if results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                metadata = results["metadatas"][0][i]
                document = results["documents"][0][i] if results["documents"] else ""
                candidates.append({
                    "tmdb_id": metadata["tmdb_id"],
                    "media_type": metadata["media_type"],
                    "title": metadata["title"],
                    "release_year": metadata.get("release_year"),
                    "genres": metadata.get("genres", ""),
                    "vote_average": metadata.get("vote_average", 0),
                    "popularity": metadata.get("popularity", 0),
                    "poster_path": metadata.get("poster_path"),
                    "document": document,
                })
        return candidates

    async def rerank(self, query: str, candidates: list[dict], user_context: str = "") -> list[dict]:
        candidates_text = "\n".join(
            f"- [tmdb_id={c['tmdb_id']}] {c['title']} ({c.get('release_year', 'N/A')}): {c['document'][:200]}"
            for c in candidates
        )
        personalization = f"User context: {user_context}" if user_context else ""
        response = await self.openai_client.chat.completions.create(
            model=self.rerank_model,
            messages=[
                {"role": "system", "content": RERANK_SYSTEM_PROMPT.format(result_count=self.result_count)},
                {"role": "user", "content": RERANK_USER_PROMPT.format(query=query, personalization=personalization, candidates=candidates_text, result_count=self.result_count)},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        try:
            parsed = json.loads(content)
            if isinstance(parsed, list):
                ranked = parsed
            elif isinstance(parsed, dict):
                ranked = parsed.get("results", parsed.get("matches", []))
            else:
                ranked = []
        except json.JSONDecodeError:
            logger.error("Failed to parse rerank response: %s", content)
            ranked = []

        candidates_by_id = {c["tmdb_id"]: c for c in candidates}
        results = []
        for item in ranked[:self.result_count]:
            tmdb_id = item["tmdb_id"]
            if tmdb_id in candidates_by_id:
                candidate = candidates_by_id[tmdb_id]
                results.append({
                    "tmdb_id": tmdb_id,
                    "media_type": candidate["media_type"],
                    "title": candidate["title"],
                    "poster_path": candidate.get("poster_path"),
                    "vote_average": candidate.get("vote_average", 0),
                    "release_year": candidate.get("release_year"),
                    "match_reason": item.get("match_reason", ""),
                })
        return results

    async def search(self, query: str, user_context: str = "") -> list[dict]:
        candidates = await self.retrieve_candidates(query)
        if not candidates:
            return []
        return await self.rerank(query, candidates, user_context)
