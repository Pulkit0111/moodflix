import asyncio
import logging

import httpx

logger = logging.getLogger(__name__)


class TMDBService:
    def __init__(self, api_key: str, base_url: str = "https://api.themoviedb.org/3"):
        self.api_key = api_key
        self.base_url = base_url
        self._client: httpx.AsyncClient | None = None

    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "accept": "application/json",
        }

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                headers=self._headers(), timeout=httpx.Timeout(30.0)
            )
        return self._client

    async def _get(self, path: str, params: dict | None = None, retries: int = 2) -> dict:
        client = await self._get_client()
        for attempt in range(retries + 1):
            try:
                response = await client.get(
                    f"{self.base_url}{path}",
                    params=params or {},
                )
                response.raise_for_status()
                return response.json()
            except httpx.ConnectError:
                if attempt < retries:
                    logger.warning("TMDB connect error on %s, retrying (%d/%d)", path, attempt + 1, retries)
                    await asyncio.sleep(0.5)
                else:
                    raise

    async def get_trending(self, page: int = 1) -> list[dict]:
        data = await self._get("/trending/all/week", params={"language": "en-US", "page": page})
        return data["results"]

    async def get_top_rated(self, media_type: str = "movie", page: int = 1) -> list[dict]:
        data = await self._get(f"/{media_type}/top_rated", params={"language": "en-US", "page": page})
        return data["results"]

    async def get_genres(self, media_type: str = "movie") -> list[dict]:
        data = await self._get(f"/genre/{media_type}/list", params={"language": "en-US"})
        return data["genres"]

    async def get_details(self, media_type: str, tmdb_id: int) -> dict:
        data = await self._get(
            f"/{media_type}/{tmdb_id}",
            params={"language": "en-US", "append_to_response": "credits,videos,watch/providers"},
        )
        return data

    async def discover(self, media_type: str, genre_id: int | None = None, page: int = 1, language: str | None = None, original_language: str | None = None) -> tuple[list[dict], int]:
        params = {"language": "en-US", "sort_by": "popularity.desc", "page": page}
        if genre_id:
            params["with_genres"] = genre_id
        if original_language:
            params["with_original_language"] = original_language
        if language:
            params["language"] = language
        data = await self._get(f"/discover/{media_type}", params=params)
        return data["results"], data["total_pages"]

    async def get_popular(self, media_type: str, page: int = 1) -> tuple[list[dict], int]:
        data = await self._get(f"/{media_type}/popular", params={"language": "en-US", "page": page})
        return data["results"], data.get("total_pages", 1)

    async def get_changes(self, media_type: str, start_date: str, page: int = 1) -> tuple[list[dict], int]:
        data = await self._get(f"/{media_type}/changes", params={"start_date": start_date, "page": page})
        return data["results"], data.get("total_pages", 1)

    async def get_keywords(self, media_type: str, tmdb_id: int) -> list[str]:
        data = await self._get(f"/{media_type}/{tmdb_id}/keywords")
        key = "keywords" if media_type == "movie" else "results"
        return [kw["name"] for kw in data.get(key, [])]

    async def get_credits(self, media_type: str, tmdb_id: int) -> list[str]:
        data = await self._get(f"/{media_type}/{tmdb_id}/credits")
        cast = data.get("cast", [])[:3]
        return [person["name"] for person in cast]
