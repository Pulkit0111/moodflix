import logging

from fastapi import APIRouter, Depends, HTTPException
from google.api_core.exceptions import PermissionDenied
from app.dependencies import verify_firebase_token
from app.services.user_service import UserService
from app.models.user import UserPreferences, WatchlistAdd, HistoryAdd

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/user", tags=["user"])

FIRESTORE_UNAVAILABLE = "Firestore is not available. Please enable the Cloud Firestore API in your GCP project."

def get_user_service() -> UserService:
    from firebase_admin import firestore
    db = firestore.client()
    return UserService(db=db)

@router.get("/profile")
async def get_profile(user: dict = Depends(verify_firebase_token), user_service: UserService = Depends(get_user_service)):
    try:
        return user_service.get_or_create_profile(uid=user["uid"], name=user.get("name"), email=user.get("email"), avatar_url=user.get("picture"))
    except PermissionDenied:
        logger.warning("Firestore API disabled – returning minimal profile")
        return {"name": user.get("name"), "email": user.get("email"), "avatar_url": user.get("picture")}

@router.get("/watchlist")
async def get_watchlist(user: dict = Depends(verify_firebase_token), user_service: UserService = Depends(get_user_service)):
    try:
        return user_service.get_watchlist(user["uid"])
    except PermissionDenied:
        logger.warning("Firestore API disabled – returning empty watchlist")
        return []

@router.post("/watchlist")
async def add_to_watchlist(item: WatchlistAdd, user: dict = Depends(verify_firebase_token), user_service: UserService = Depends(get_user_service)):
    try:
        user_service.add_to_watchlist(uid=user["uid"], tmdb_id=item.tmdb_id, media_type=item.media_type, title=item.title, poster_path=item.poster_path)
        return {"status": "added"}
    except PermissionDenied:
        raise HTTPException(status_code=503, detail=FIRESTORE_UNAVAILABLE)

@router.delete("/watchlist/{tmdb_id}")
async def remove_from_watchlist(tmdb_id: int, user: dict = Depends(verify_firebase_token), user_service: UserService = Depends(get_user_service)):
    try:
        user_service.remove_from_watchlist(user["uid"], tmdb_id)
        return {"status": "removed"}
    except PermissionDenied:
        raise HTTPException(status_code=503, detail=FIRESTORE_UNAVAILABLE)

@router.get("/history")
async def get_history(user: dict = Depends(verify_firebase_token), user_service: UserService = Depends(get_user_service)):
    try:
        return user_service.get_history(user["uid"])
    except PermissionDenied:
        logger.warning("Firestore API disabled – returning empty history")
        return []

@router.post("/history")
async def add_to_history(item: HistoryAdd, user: dict = Depends(verify_firebase_token), user_service: UserService = Depends(get_user_service)):
    try:
        user_service.add_to_history(uid=user["uid"], tmdb_id=item.tmdb_id, media_type=item.media_type, title=item.title, rating=item.rating)
        return {"status": "added"}
    except PermissionDenied:
        raise HTTPException(status_code=503, detail=FIRESTORE_UNAVAILABLE)

@router.get("/preferences")
async def get_preferences(user: dict = Depends(verify_firebase_token), user_service: UserService = Depends(get_user_service)):
    try:
        return user_service.get_preferences(user["uid"])
    except PermissionDenied:
        logger.warning("Firestore API disabled – returning empty preferences")
        return {"favorite_genres": [], "disliked_genres": [], "preferred_decades": []}

@router.put("/preferences")
async def update_preferences(prefs: UserPreferences, user: dict = Depends(verify_firebase_token), user_service: UserService = Depends(get_user_service)):
    try:
        user_service.update_preferences(uid=user["uid"], favorite_genres=prefs.favorite_genres, disliked_genres=prefs.disliked_genres, preferred_decades=prefs.preferred_decades)
        return {"status": "updated"}
    except PermissionDenied:
        raise HTTPException(status_code=503, detail=FIRESTORE_UNAVAILABLE)

@router.get("/search-history")
async def get_search_history(user: dict = Depends(verify_firebase_token), user_service: UserService = Depends(get_user_service)):
    try:
        return user_service.get_search_history(user["uid"])
    except PermissionDenied:
        logger.warning("Firestore API disabled – returning empty search history")
        return []
