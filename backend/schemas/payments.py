from __future__ import annotations

from typing import Optional, List
from pydantic import BaseModel


class CodeCreateRequest(BaseModel):
	ttl_minutes: Optional[int] = None


class CodeCreateResponse(BaseModel):
	code: str
	status: str
	expires_at: Optional[str] = None


class CodeListItem(BaseModel):
	code: str
	status: str
	expires_at: Optional[str] = None
	redeemed_by: Optional[str] = None


class CodesListEnvelope(BaseModel):
	items: List[CodeListItem]


class RedeemRequest(BaseModel):
	code: str


class RedeemResponse(BaseModel):
	message: str
	code: str


