import logging

from fastapi import APIRouter, Depends
from openai import AsyncOpenAI

from app.config import settings
from app.dependencies import verify_firebase_token, get_chroma_collection
from app.services.taste_service import TasteService
from app.services.user_service import UserService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/user", tags=["taste"])


def _get_taste_service() -> TasteService:
    from firebase_admin import firestore
    db = firestore.client()
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    user_service = UserService(db=db)
    collection = get_chroma_collection()
    return TasteService(openai_client=client, user_service=user_service, collection=collection)


@router.get("/taste-dna")
async def get_taste_dna(
    user: dict = Depends(verify_firebase_token),
    taste_service: TasteService = Depends(_get_taste_service),
):
    try:
        result = await taste_service.analyze_taste(user["uid"])
    except Exception as e:
        logger.error("Taste analysis error: %s", e)
        return {"status": "error", "message": "Failed to analyze taste"}

    if result is None:
        return {"status": "insufficient_data", "minimum_required": 5}

    return result
