from datetime import datetime, timezone
from typing import Optional

from pydantic import BaseModel, Field


class ChatMessageBase(BaseModel):
    role: str = Field(description="user or assistant")
    content: str

    model_config = {"populate_by_name": True}


class ChatMessageCreate(ChatMessageBase):
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ChatMessageUpdate(BaseModel):
    content: Optional[str] = None

    model_config = {"populate_by_name": True}


class ChatMessageResponse(ChatMessageBase):
    id: str
    timestamp: datetime
