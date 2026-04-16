import logging

from fastapi import APIRouter, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.dependencies import verify_firebase_token, get_chroma_collection
from app.models.search import SearchRequest, SearchResponse, SearchResult
from app.services.search_service import SearchService
from app.services.user_service import UserService
from app.services.embedding_service import EmbeddingService
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["search"])
limiter = Limiter(key_func=get_remote_address)

def get_search_service() -> SearchService:
    embedding_service = EmbeddingService(api_key=settings.openai_api_key, model=settings.embedding_model)
    return SearchService(
        collection=get_chroma_collection(), embedding_service=embedding_service,
        rerank_model=settings.rerank_model, openai_api_key=settings.openai_api_key,
        candidate_count=settings.candidate_count, result_count=settings.result_count,
    )

def get_user_service() -> UserService:
    from firebase_admin import firestore
    db = firestore.client()
    return UserService(db=db)

def _build_user_context(user_service: UserService, uid: str) -> str:
    try:
        prefs = user_service.get_preferences(uid)
        history = user_service.get_history(uid)
    except Exception as e:
        logger.warning("Failed to fetch user context from Firestore: %s", e)
        return ""
    parts = []
    if prefs.get("favorite_genres"):
        parts.append(f"Likes: {', '.join(prefs['favorite_genres'])}")
    if prefs.get("disliked_genres"):
        parts.append(f"Dislikes: {', '.join(prefs['disliked_genres'])}")
    if history:
        seen_titles = [h["title"] for h in history[-20:]]
        parts.append(f"Already watched: {', '.join(seen_titles)}")
    return ". ".join(parts)

@router.post("/search", response_model=SearchResponse)
@limiter.limit("20/hour")
async def search(
    request: Request,
    body: SearchRequest,
    user: dict = Depends(verify_firebase_token),
    search_service: SearchService = Depends(get_search_service),
    user_service: UserService = Depends(get_user_service),
):
    user_context = _build_user_context(user_service, user["uid"])
    results = await search_service.search(body.query, user_context, body.filter_text or "")
    try:
        user_service.add_search_query(user["uid"], body.query)
    except Exception as e:
        logger.warning("Failed to save search query to Firestore: %s", e)
    return SearchResponse(query=request.query, results=[SearchResult(**r) for r in results])
