from __future__ import annotations

from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class GroupCreate(BaseModel):
	name: str = Field(..., description="Group display name.")
	description: Optional[str] = Field(default=None, description="Optional group description.")


class GroupUpdate(BaseModel):
	name: str = Field(..., description="Updated group name.")
	description: Optional[str] = Field(default=None, description="Updated description.")


class GroupListItem(BaseModel):
	id: str = Field(..., description="Group id.")
	name: str = Field(..., description="Group name.")
	description: Optional[str] = Field(default=None, description="Group description.")


class GroupDetail(BaseModel):
	id: str = Field(..., description="Group id.")
	name: str = Field(..., description="Group name.")
	description: Optional[str] = Field(default=None, description="Group description.")
	created_by: str = Field(..., description="User id who created the group.")
	created_at: Optional[datetime] = Field(default=None, description="UTC creation timestamp.")


class MembershipItem(BaseModel):
	id: str = Field(..., description="Membership id.")
	userId: str = Field(..., description="User id of the member.")
	role: str = Field(..., description="Group role for the member.")
	full_name: Optional[str] = Field(default=None, description="Member full name, if available.")
	email: Optional[str] = Field(default=None, description="Member email, if available.")
	age: Optional[int] = Field(default=None, description="Member age, if available.")


class GroupsListEnvelope(BaseModel):
	items: List[GroupListItem] = Field(..., description="Groups visible to the current user.")


class GroupDetailEnvelope(BaseModel):
	data: GroupDetail = Field(..., description="Detailed group object.")


class MembershipsListEnvelope(BaseModel):
	items: List[MembershipItem] = Field(..., description="Memberships in the group.")


class ActionEnvelope(BaseModel):
	message: str = Field(..., description="Action outcome message.")


