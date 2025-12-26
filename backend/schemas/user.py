from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, EmailStr
from backend.schemas.common import Role, Timestamped


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Role


class UserUpdate(BaseModel):
    username: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[Role] = None


class UserResponse(Timestamped):
    id: UUID
    username: str
    email: EmailStr
    role: Role
    corpus_uri: str
    chat_history_uri: Optional[str] = None
    group_ids: List[UUID] = []


