from uuid import UUID
from typing import Optional
from pydantic import BaseModel


class MessageCreate(BaseModel):
    sender_id: UUID
    content: str


class MessageUpdate(BaseModel):
    content: Optional[str] = None


