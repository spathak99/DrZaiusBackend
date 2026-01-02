"""Pydantic schemas for redaction endpoints."""
from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class RedactionFinding(BaseModel):
	"""Single DLP finding with info type and optional quote snippet."""
	info_type: str = Field(..., description="DLP info type name (e.g., PHONE_NUMBER).")
	quote: Optional[str] = Field(default=None, description="Original snippet identified by DLP, if available.")


class RedactionResult(BaseModel):
	"""Aggregated result for redaction."""
	findings: List[RedactionFinding] = Field(default_factory=list, description="All detected findings.")
	redacted_types: List[str] = Field(default_factory=list, description="Info type names that were redacted.")


class RedactUploadResponse(BaseModel):
	"""Generic response for upload/redaction flows."""
	message: str = Field(..., description="Human-readable status or message.")
	recipientId: str = Field(..., description="Target recipient identifier.")
	data: dict = Field(..., description="Additional data payload.")


class RedactionTestRequest(BaseModel):
	"""Payload for inline redaction tests."""
	text: str = Field(..., description="Text content to test redaction on.")


class RedactionTestResponse(BaseModel):
	"""Result for inline redaction tests with redacted text."""
	input_len: int = Field(..., description="Input byte length.")
	output_len: int = Field(..., description="Output byte length after redaction.")
	findings: List[RedactionFinding] = Field(default_factory=list, description="All detected findings.")
	redactedText: str = Field(..., description="Redacted text output.")


class RedactionStatusResponse(BaseModel):
	"""Status report on DLP configuration and client readiness."""
	enableDlp: bool = Field(..., description="Whether DLP feature flag is enabled.")
	projectId: str = Field(..., description="Configured GCP project id.")
	location: str = Field(..., description="Configured DLP location/region.")
	clientReady: bool = Field(..., description="True if DLP client is initialized.")


class RedactionTextFileResponse(BaseModel):
	"""Response for text file redaction."""
	redactedText: str = Field(..., description="Redacted text content.")
	findings: List[RedactionFinding] = Field(default_factory=list, description="Detected findings.")

