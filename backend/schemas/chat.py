from uuid import UUID
from typing import Optional
from pydantic import BaseModel
from backend.schemas.common import Timestamped


class ChatCreate(BaseModel):
    name: Optional[str] = None
    created_by: Optional[UUID] = None


class ChatUpdate(BaseModel):
    name: Optional[str] = None


class ChatResponse(Timestamped):
    id: UUID
    name: Optional[str] = None
    created_by: Optional[UUID] = None

