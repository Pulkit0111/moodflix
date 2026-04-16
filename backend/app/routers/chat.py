import logging

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from openai import AsyncOpenAI

from app.config import settings
from app.dependencies import verify_firebase_token, get_chroma_collection
from app.models.chat import ChatRequest
from app.services.chat_service import ChatService
from app.services.search_service import SearchService
from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["chat"])
limiter = Limiter(key_func=get_remote_address)


def _get_chat_service() -> ChatService:
    collection = get_chroma_collection()
    embedding_service = EmbeddingService(api_key=settings.openai_api_key, model=settings.embedding_model)
    search_service = SearchService(
        collection=collection, embedding_service=embedding_service,
        rerank_model=settings.rerank_model, openai_api_key=settings.openai_api_key,
        candidate_count=settings.candidate_count, result_count=settings.result_count,
    )
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    return ChatService(search_service=search_service, openai_client=client)


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
        if prefs.get("disliked_genres"):
            parts.append(f"Dislikes: {', '.join(prefs['disliked_genres'])}")
        if history:
            seen = [h["title"] for h in history[-10:]]
            parts.append(f"Recently watched: {', '.join(seen)}")
        return ". ".join(parts)
    except Exception:
        return ""


@router.post("/chat")
@limiter.limit("30/hour")
async def chat(request: Request, body: ChatRequest, user: dict = Depends(verify_firebase_token)):
    service = _get_chat_service()
    user_context = _build_user_context(user["uid"])
    messages = [{"role": m.role, "content": m.content} for m in body.messages]

    async def event_stream():
        async for chunk in service.stream_chat(messages, user_context):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
