from __future__ import annotations

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel


class GroupCreate(BaseModel):
	name: str
	description: Optional[str] = None


class GroupUpdate(BaseModel):
	name: str
	description: Optional[str] = None


class GroupListItem(BaseModel):
	id: str
	name: str
	description: Optional[str] = None


class GroupDetail(BaseModel):
	id: str
	name: str
	description: Optional[str] = None
	created_by: str
	created_at: Optional[datetime] = None


class MembershipItem(BaseModel):
	id: str
	userId: str
	role: str
	full_name: Optional[str] = None
	email: Optional[str] = None
	age: Optional[int] = None


class GroupsListEnvelope(BaseModel):
	items: List[GroupListItem]


class GroupDetailEnvelope(BaseModel):
	data: GroupDetail


class MembershipsListEnvelope(BaseModel):
	items: List[MembershipItem]


class ActionEnvelope(BaseModel):
	message: str


