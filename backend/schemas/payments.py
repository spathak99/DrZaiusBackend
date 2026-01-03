from __future__ import annotations

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class CodeCreateRequest(BaseModel):
	ttl_minutes: Optional[int] = Field(default=None, description="How long (minutes) the code remains valid.")


class CodeCreateResponse(BaseModel):
	code: str = Field(..., description="Generated code value.")
	status: str = Field(..., description="Current status of the code.")
	expires_at: Optional[datetime] = Field(default=None, description="UTC expiration timestamp, if set.")


class CodeListItem(BaseModel):
	code: str = Field(..., description="Code value.")
	status: str = Field(..., description="Status (active, expired, redeemed).")
	expires_at: Optional[datetime] = Field(default=None, description="UTC expiration timestamp, if set.")
	redeemed_by: Optional[str] = Field(default=None, description="User id who redeemed the code, if any.")


class CodesListEnvelope(BaseModel):
	items: List[CodeListItem] = Field(..., description="List of codes.")


class RedeemRequest(BaseModel):
	code: str = Field(..., description="Code to redeem.")


class RedeemResponse(BaseModel):
	message: str = Field(..., description="Outcome of the redeem operation.")
	code: str = Field(..., description="Redeemed code.")


