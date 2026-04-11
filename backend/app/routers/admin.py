import json
import os
from fastapi import APIRouter, Depends, BackgroundTasks
from app.dependencies import verify_firebase_token
from app.config import settings

router = APIRouter(prefix="/api/admin", tags=["admin"])

SYNC_STATE_PATH = os.path.normpath(os.path.join(settings.chroma_persist_dir, "..", "sync_state.json"))

def get_sync_state() -> dict:
    path = os.path.normpath(SYNC_STATE_PATH)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {"last_sync": None, "total_movies": 0, "total_tv": 0}

@router.get("/sync/status")
async def sync_status(user: dict = Depends(verify_firebase_token)):
    state = get_sync_state()
    collection_count = 0
    try:
        from app.dependencies import get_chroma_collection
        collection_count = get_chroma_collection().count()
    except Exception:
        pass
    return {**state, "collection_count": collection_count}

@router.post("/sync/run")
async def trigger_sync(background_tasks: BackgroundTasks, user: dict = Depends(verify_firebase_token)):
    from app.workers.tmdb_sync import run_sync
    background_tasks.add_task(run_sync)
    return {"status": "sync_started"}
