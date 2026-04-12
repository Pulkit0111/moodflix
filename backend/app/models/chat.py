from pydantic import BaseModel
from app.models.media import MediaSummary


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]


class ChatRecommendation(MediaSummary):
    pitch: str
