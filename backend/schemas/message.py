from uuid import UUID
from typing import Optional
from pydantic import BaseModel
from backend.schemas.common import Timestamped


class MessageCreate(BaseModel):
    sender_id: UUID
    content: str


class MessageUpdate(BaseModel):
    content: Optional[str] = None


class MessageResponse(Timestamped):
    id: UUID
    chat_id: UUID
    sender_id: Optional[UUID] = None
    content: Optional[str] = None

