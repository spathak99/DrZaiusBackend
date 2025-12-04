from typing import Optional
from pydantic import BaseModel


class SecurityPolicyCreate(BaseModel):
    name: str
    rules: Optional[dict] = None


class SecurityPolicyUpdate(BaseModel):
    name: Optional[str] = None
    rules: Optional[dict] = None


class KeyGenerateRequest(BaseModel):
    algorithm: str = "rsa-2048"


