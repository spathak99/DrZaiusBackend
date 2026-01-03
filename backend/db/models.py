"""Aggregated ORM models (compat shim). New definitions live under backend.db.entities.*"""
from __future__ import annotations

from backend.db.base import Base  # re-export Base
from backend.db.entities import (
	User,
	RecipientCaregiverAccess,
	Chat,
	ChatParticipant,
	Message,
	File,
	FileAccess,
	Invitation,
	Group,
	GroupMembership,
	GroupPaymentCode,
	GroupMemberInvite,
	Dependent,
)

__all__ = [
	"Base",
	"User",
	"RecipientCaregiverAccess",
	"Chat",
	"ChatParticipant",
	"Message",
	"File",
	"FileAccess",
	"Invitation",
	"Group",
	"GroupMembership",
	"GroupPaymentCode",
	"GroupMemberInvite",
	"Dependent",
]


