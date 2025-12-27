from uuid import UUID
from typing import Optional
from pydantic import BaseModel, EmailStr
from backend.schemas.common import Role, AccountType


class SignupRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Role
    # Profile (optional at signup)
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    age: Optional[int] = None
    country: Optional[str] = None
    avatar_uri: Optional[str] = None
    corpus_uri: str
    account_type: Optional[AccountType] = None
    group_id: Optional[UUID] = None
    gcp_project_id: Optional[str] = None
    temp_bucket: Optional[str] = None
    payment_info: Optional[dict] = None
    chat_history_uri: Optional[str] = None


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MeResponse(BaseModel):
    id: UUID
    username: str
    email: EmailStr
    role: Role


