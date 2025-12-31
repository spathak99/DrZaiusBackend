from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, EmailStr


class GroupMemberInviteCreate(BaseModel):
	email: EmailStr
	full_name: Optional[str] = None


class GroupMemberInviteItem(BaseModel):
	id: str
	invited_email: EmailStr
	invited_full_name: Optional[str] = None
	status: str
	acceptUrl: Optional[str] = None


class GroupMemberInvitesEnvelope(BaseModel):
	items: List[GroupMemberInviteItem]


class GroupMemberInviteCreatedEnvelope(BaseModel):
	message: str
	data: GroupMemberInviteItem


