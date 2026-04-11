import logging
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import search, browse, detail, user, admin

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.dependencies import init_firebase
    try:
        init_firebase()
        logger.info("Firebase initialized")
    except Exception as e:
        logger.warning("Firebase init skipped: %s", e)
    from app.workers.tmdb_sync import run_sync
    scheduler.add_job(run_sync, "cron", hour=3, id="tmdb_sync")
    scheduler.start()
    logger.info("Scheduler started")
    yield
    scheduler.shutdown()
    logger.info("Scheduler stopped")

app = FastAPI(title="MoodFlix API", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(search.router)
app.include_router(browse.router)
app.include_router(detail.router)
app.include_router(user.router)
app.include_router(admin.router)

@app.get("/api/health")
async def health():
    return {"status": "ok"}
