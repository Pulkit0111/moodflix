from fastapi import APIRouter, Depends
from app.services.tmdb_service import TMDBService
from app.dependencies import get_chroma_collection
from app.config import settings

router = APIRouter(prefix="/api", tags=["detail"])

def get_tmdb_service() -> TMDBService:
    return TMDBService(api_key=settings.tmdb_api_key, base_url=settings.tmdb_base_url)

def get_similar_from_chroma(media_type: str, tmdb_id: int, n: int = 10) -> list[dict]:
    collection = get_chroma_collection()
    doc_id = f"{media_type}_{tmdb_id}"
    try:
        existing = collection.get(ids=[doc_id], include=["embeddings"])
    except Exception:
        return []
    if not existing["ids"]:
        return []
    embedding = existing["embeddings"][0]
    results = collection.query(query_embeddings=[embedding], n_results=n + 1)
    similar = []
    if results["ids"] and results["ids"][0]:
        for i, rid in enumerate(results["ids"][0]):
            if rid == doc_id:
                continue
            meta = results["metadatas"][0][i]
            similar.append({
                "tmdb_id": meta["tmdb_id"], "media_type": meta["media_type"],
                "title": meta["title"], "poster_path": meta.get("poster_path"),
                "vote_average": meta.get("vote_average", 0), "release_year": meta.get("release_year"),
            })
            if len(similar) >= n:
                break
    return similar

@router.get("/title/{media_type}/{tmdb_id}")
async def get_details(media_type: str, tmdb_id: int, tmdb: TMDBService = Depends(get_tmdb_service)):
    return await tmdb.get_details(media_type, tmdb_id)

@router.get("/title/{media_type}/{tmdb_id}/similar")
async def get_similar(media_type: str, tmdb_id: int):
    return get_similar_from_chroma(media_type, tmdb_id)
