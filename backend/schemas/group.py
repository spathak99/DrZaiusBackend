from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from backend.schemas.common import Timestamped


class GroupCreate(BaseModel):
    name: str
    description: Optional[str] = None


class GroupResponse(Timestamped):
    id: UUID
    name: str
    description: Optional[str] = None
    created_by: UUID


class GroupMemberAdd(BaseModel):
    user_id: UUID
    role: Optional[str] = None  # "admin" | "member"


class GroupMemberResponse(Timestamped):
    id: UUID
    group_id: UUID
    user_id: UUID
    role: Optional[str] = None


