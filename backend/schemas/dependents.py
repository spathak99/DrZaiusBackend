from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, EmailStr


class DependentCreate(BaseModel):
	full_name: Optional[str] = None
	dob: Optional[str] = None  # ISO date string (YYYY-MM-DD)
	email: Optional[EmailStr] = None


class DependentItem(BaseModel):
	id: str
	full_name: Optional[str] = None
	dob: Optional[str] = None
	email: Optional[EmailStr] = None
	guardian_user_id: str


class DependentsEnvelope(BaseModel):
	items: List[DependentItem]


class DependentConvertRequest(BaseModel):
	email: Optional[EmailStr] = None


class DependentConvertResponse(BaseModel):
	message: str
	userId: str


