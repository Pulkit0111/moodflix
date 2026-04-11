from openai import AsyncOpenAI


class EmbeddingService:
    def __init__(self, api_key: str, model: str = "text-embedding-3-small"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def embed_text(self, text: str) -> list[float]:
        response = await self.client.embeddings.create(model=self.model, input=text)
        return response.data[0].embedding

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        response = await self.client.embeddings.create(model=self.model, input=texts)
        return [item.embedding for item in response.data]

    def build_movie_text(self, title: str, overview: str, genres: list[str], keywords: list[str], cast: list[str]) -> str:
        parts = [f"{title}. {overview}"]
        if genres:
            parts.append(f"Genres: {', '.join(genres)}.")
        if keywords:
            parts.append(f"Keywords: {', '.join(keywords)}.")
        if cast:
            parts.append(f"Cast: {', '.join(cast)}.")
        return " ".join(parts)
