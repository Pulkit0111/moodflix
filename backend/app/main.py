from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import browse, detail, search, admin, user

app = FastAPI(title="MoodFlix API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health():
    return {"status": "ok"}


app.include_router(browse.router)
app.include_router(search.router)
app.include_router(detail.router)
app.include_router(user.router)
app.include_router(admin.router)
