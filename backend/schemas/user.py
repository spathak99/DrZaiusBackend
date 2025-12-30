from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, EmailStr
from backend.schemas.common import Role, Timestamped, AccountType
from typing import List


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
    # Profile
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    age: Optional[int] = None
    country: Optional[str] = None
    avatar_uri: Optional[str] = None
    corpus_uri: str
    chat_history_uri: Optional[str] = None
    group_ids: List[UUID] = []
    account_type: Optional[AccountType] = None
    group_id: Optional[UUID] = None
    gcp_project_id: Optional[str] = None
    temp_bucket: Optional[str] = None
    payment_info: Optional[dict] = None


class UserSettingsUpdate(BaseModel):
    # Profile
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    age: Optional[int] = None
    country: Optional[str] = None
    avatar_uri: Optional[str] = None
    corpus_uri: Optional[str] = None
    chat_history_uri: Optional[str] = None
    account_type: Optional[AccountType] = None
    gcp_project_id: Optional[str] = None
    temp_bucket: Optional[str] = None
    payment_info: Optional[dict] = None


class UsersListEnvelope(BaseModel):
    items: List[UserResponse]

