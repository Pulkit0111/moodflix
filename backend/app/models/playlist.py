from pydantic import BaseModel
from app.models.media import MediaSummary


class MoodPlaylist(BaseModel):
    id: str
    name: str
    description: str
    mood_key: str
    items: list[MediaSummary]
    generated_at: str
