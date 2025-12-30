from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel


class CaregiverListItem(BaseModel):
	id: str
	full_name: Optional[str] = None
	role: Optional[str] = None


class CaregiversListEnvelope(BaseModel):
	items: List[CaregiverListItem]


class RecipientListItem(BaseModel):
	id: str
	full_name: Optional[str] = None


class RecipientsListEnvelope(BaseModel):
	items: List[RecipientListItem]


