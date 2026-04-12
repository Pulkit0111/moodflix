import logging

from fastapi import APIRouter, Depends
from openai import AsyncOpenAI
from pydantic import BaseModel

from app.config import settings
from app.dependencies import verify_firebase_token, get_chroma_collection
from app.services.pitch_service import PitchService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["pitch"])


def _get_pitch_service() -> PitchService:
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    return PitchService(openai_client=client)


def _build_user_context(uid: str) -> str:
    try:
        from firebase_admin import firestore
        db = firestore.client()
        from app.services.user_service import UserService
        user_service = UserService(db=db)
        prefs = user_service.get_preferences(uid)
        history = user_service.get_history(uid)
        parts = []
        if prefs.get("favorite_genres"):
            parts.append(f"Likes: {', '.join(prefs['favorite_genres'])}")
        if history:
            seen = [h["title"] for h in history[-10:]]
            parts.append(f"Recently enjoyed: {', '.join(seen)}")
        return ". ".join(parts)
    except Exception:
        return ""


@router.get("/pitch/{media_type}/{tmdb_id}")
async def get_pitch(
    media_type: str, tmdb_id: int,
    user: dict = Depends(verify_firebase_token),
    pitch_service: PitchService = Depends(_get_pitch_service),
):
    user_context = _build_user_context(user["uid"])
    if not user_context:
        return {"pitch": ""}

    collection = get_chroma_collection()
    doc_id = f"{media_type}_{tmdb_id}"
    try:
        result = collection.get(ids=[doc_id], include=["metadatas", "documents"])
        if not result["ids"]:
            return {"pitch": ""}
        meta = result["metadatas"][0]
        overview = (result["documents"][0] or "")[:200]
    except Exception:
        return {"pitch": ""}

    pitch = await pitch_service.generate_pitch(
        title=meta.get("title", ""),
        overview=overview,
        genres=meta.get("genres", ""),
        user_context=user_context,
    )
    return {"pitch": pitch}


class BatchPitchRequest(BaseModel):
    items: list[dict]


@router.post("/pitches")
async def get_pitches_batch(
    request: BatchPitchRequest,
    user: dict = Depends(verify_firebase_token),
    pitch_service: PitchService = Depends(_get_pitch_service),
):
    user_context = _build_user_context(user["uid"])
    if not user_context or not request.items:
        return {"pitches": {}}

    # Enrich items with overview from ChromaDB
    collection = get_chroma_collection()
    enriched = []
    for item in request.items[:20]:
        doc_id = f"{item.get('media_type', 'movie')}_{item['tmdb_id']}"
        try:
            result = collection.get(ids=[doc_id], include=["metadatas", "documents"])
            if result["ids"]:
                enriched.append({
                    "tmdb_id": item["tmdb_id"],
                    "title": result["metadatas"][0].get("title", ""),
                    "overview": (result["documents"][0] or "")[:100],
                    "genres": result["metadatas"][0].get("genres", ""),
                })
        except Exception:
            pass

    pitches = await pitch_service.generate_pitches_batch(enriched, user_context)
    return {"pitches": pitches}
