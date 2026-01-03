from __future__ import annotations

from typing import Optional, Dict, Any
from fastapi import HTTPException, status


class AppError(Exception):
	"""Base application error carrying a stable code and optional HTTP status."""
	def __init__(self, code: str, message: Optional[str] = None, *, status_code: Optional[int] = None, extra: Optional[Dict[str, Any]] = None) -> None:
		super().__init__(message or code)
		self.code = code
		self.status_code = status_code
		self.extra = extra or {}


def to_http(exc: AppError) -> HTTPException:
	"""Convert AppError to HTTPException with stable detail code."""
	return HTTPException(status_code=exc.status_code or status.HTTP_400_BAD_REQUEST, detail=exc.code)


