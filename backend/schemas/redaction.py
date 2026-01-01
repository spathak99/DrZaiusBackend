from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel


class RedactionFinding(BaseModel):
	info_type: str
	quote: Optional[str] = None


class RedactionResult(BaseModel):
	findings: List[RedactionFinding] = []
	redacted_types: List[str] = []


class RedactUploadResponse(BaseModel):
	message: str
	recipientId: str
	data: dict


class RedactionTestRequest(BaseModel):
	text: str


class RedactionTestResponse(BaseModel):
	input_len: int
	output_len: int
	findings: List[RedactionFinding] = []

