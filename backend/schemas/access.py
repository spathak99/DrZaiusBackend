from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel

from backend.schemas.common import AccessLevel


class CaregiverAccessItem(BaseModel):
	caregiverId: str
	access_level: Optional[AccessLevel] = None


class RecipientAccessItem(BaseModel):
	recipientId: str
	access_level: Optional[AccessLevel] = None


class RecipientCaregiversEnvelope(BaseModel):
	recipientId: str
	items: List[CaregiverAccessItem]


class CaregiverRecipientsEnvelope(BaseModel):
	caregiverId: str
	items: List[RecipientAccessItem]


class CaregiverRecipientGetResponse(BaseModel):
	caregiverId: str
	recipientId: str
	access_level: Optional[AccessLevel] = None


class AccessMutateEnvelope(BaseModel):
	message: str
	recipientId: str
	caregiverId: str
	access_level: Optional[AccessLevel] = None

from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from backend.schemas.common import AccessLevel, Timestamped


class CaregiverAccessUpdate(BaseModel):
    access_level: AccessLevel


class CaregiverAssign(BaseModel):
    caregiver_id: UUID
    access_level: Optional[AccessLevel] = None


class CaregiverAccessResponse(Timestamped):
    id: UUID
    recipient_id: UUID
    caregiver_id: UUID
    access_level: Optional[AccessLevel] = None


