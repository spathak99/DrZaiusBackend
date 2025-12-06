from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from backend.schemas.common import Timestamped


class SecurityPolicyCreate(BaseModel):
    name: str
    rules: Optional[dict] = None


class SecurityPolicyUpdate(BaseModel):
    name: Optional[str] = None
    rules: Optional[dict] = None


class KeyGenerateRequest(BaseModel):
    algorithm: str = "rsa-2048"


class SecurityPolicyResponse(Timestamped):
    id: UUID
    name: str
    rules: Optional[dict] = None


class KeyPairResponse(BaseModel):
    key_id: UUID
    algorithm: str
    public_key_pem: str


