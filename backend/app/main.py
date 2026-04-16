import logging
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.config import settings
from app.routers import search, browse, detail, user, admin, playlist, chat, pitch, taste

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()
limiter = Limiter(key_func=get_remote_address)

@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.dependencies import init_firebase
    try:
        init_firebase()
        logger.info("Firebase initialized")
    except Exception as e:
        logger.warning("Firebase init skipped: %s", e)
    from app.workers.tmdb_sync import run_sync
    scheduler.add_job(run_sync, "cron", hour=3, id="tmdb_sync", max_instances=1, coalesce=True, misfire_grace_time=3600)
    scheduler.start()
    logger.info("Scheduler started")
    yield
    scheduler.shutdown()
    logger.info("Scheduler stopped")

app = FastAPI(title="MoodFlix API", version="0.1.0", lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router)
app.include_router(browse.router)
app.include_router(detail.router)
app.include_router(user.router)
app.include_router(admin.router)
app.include_router(playlist.router)
app.include_router(chat.router)
app.include_router(pitch.router)
app.include_router(taste.router)

@app.get("/api/health")
async def health():
    return {"status": "ok"}
