from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field


class DependentCreate(BaseModel):
	full_name: Optional[str] = Field(default=None, description="Full name of the dependent.")
	dob: Optional[str] = Field(default=None, description="ISO date string (YYYY-MM-DD).")
	email: Optional[EmailStr] = Field(default=None, description="Email address, if available.")


class DependentItem(BaseModel):
	id: str = Field(..., description="Dependent user id.")
	full_name: Optional[str] = Field(default=None, description="Full name.")
	dob: Optional[str] = Field(default=None, description="Date of birth (ISO).")
	email: Optional[EmailStr] = Field(default=None, description="Email address.")
	guardian_user_id: str = Field(..., description="Guardian user id.")


class DependentsEnvelope(BaseModel):
	items: List[DependentItem] = Field(..., description="List of dependents.")


class DependentConvertRequest(BaseModel):
	email: Optional[EmailStr] = Field(default=None, description="Invite email to use for the new account.")


class DependentConvertResponse(BaseModel):
	message: str = Field(..., description="Outcome of conversion.")
	userId: str = Field(..., description="Created user id.")


