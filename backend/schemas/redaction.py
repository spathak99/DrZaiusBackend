from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class RedactionFinding(BaseModel):
	info_type: str
	quote: Optional[str] = None


class RedactionResult(BaseModel):
	findings: List[RedactionFinding] = Field(default_factory=list)
	redacted_types: List[str] = Field(default_factory=list)


class RedactUploadResponse(BaseModel):
	message: str
	recipientId: str
	data: dict


class RedactionTestRequest(BaseModel):
	text: str


class RedactionTestResponse(BaseModel):
	input_len: int
	output_len: int
	findings: List[RedactionFinding] = Field(default_factory=list)
	redactedText: str


class RedactionStatusResponse(BaseModel):
	enableDlp: bool
	projectId: str
	location: str
	clientReady: bool


class RedactionTextFileResponse(BaseModel):
	redactedText: str
	findings: List[RedactionFinding] = Field(default_factory=list)

