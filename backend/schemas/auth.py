from uuid import UUID
from pydantic import BaseModel, EmailStr
from backend.schemas.common import Role


class SignupRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Role


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


