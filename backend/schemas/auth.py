"""Pydantic schemas for authentication flows."""
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from backend.core.constants import Messages
from backend.schemas.common import Role, AccountType


class SignupRequest(BaseModel):
    """Request payload to create a new user account."""
    username: str = Field(..., description="Desired username (unique).")
    email: EmailStr = Field(..., description="User email (unique).")
    password: str = Field(..., description="Password for the new account.")
    role: Role = Field(..., description="Initial role for the account.")
    # Profile (optional at signup)
    full_name: Optional[str] = Field(default=None, description="Optional full name.")
    phone_number: Optional[str] = Field(default=None, description="Optional phone number.")
    age: Optional[int] = Field(default=None, description="Optional age.")
    country: Optional[str] = Field(default=None, description="Optional country.")
    avatar_uri: Optional[str] = Field(default=None, description="Optional avatar URI.")
    corpus_uri: str = Field(..., description="User corpus URI (storage path).")
    account_type: Optional[AccountType] = Field(default=None, description="Account type (individual or group).")
    group_id: Optional[UUID] = Field(default=None, description="Optional group id for group accounts.")
    gcp_project_id: Optional[str] = Field(default=None, description="Optional GCP project id for user context.")
    temp_bucket: Optional[str] = Field(default=None, description="Optional temporary bucket for uploads.")
    payment_info: Optional[dict] = Field(default=None, description="Optional payment metadata.")
    chat_history_uri: Optional[str] = Field(default=None, description="Optional chat history URI.")


class LoginRequest(BaseModel):
    """Request payload to authenticate via username/email and password."""
    username: str = Field(..., description="Username or email.")
    password: str = Field(..., description="Account password.")


class ChangePasswordRequest(BaseModel):
    """Request payload to change password."""
    current_password: str = Field(..., description="Existing password.")
    new_password: str = Field(..., description="New password.")


class TokenResponse(BaseModel):
    """Response containing the bearer token."""
    access_token: str = Field(..., description="Signed access token (bearer).")
    token_type: str = Field(default=Messages.TOKEN_TYPE_BEARER, description="Token type indicator.")


class MeResponse(BaseModel):
    """Subset of user profile returned by /auth/me."""
    id: UUID = Field(..., description="User id.")
    username: str = Field(..., description="Username.")
    email: EmailStr = Field(..., description="Email address.")
    role: Role = Field(..., description="Assigned role.")


