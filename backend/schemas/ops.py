from __future__ import annotations

from typing import Any, Dict
from pydantic import BaseModel


class HealthzResponse(BaseModel):
	status: str


class ReadyzResults(BaseModel):
	db: str
	enablePipeline: bool
	enableDlp: bool


class ReadyzResponse(BaseModel):
	status: str
	results: ReadyzResults


