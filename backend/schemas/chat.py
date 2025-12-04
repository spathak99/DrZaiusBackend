from uuid import UUID
from typing import Optional
from pydantic import BaseModel


class ChatCreate(BaseModel):
    name: Optional[str] = None
    created_by: Optional[UUID] = None


class ChatUpdate(BaseModel):
    name: Optional[str] = None


