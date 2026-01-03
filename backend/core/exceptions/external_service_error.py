from __future__ import annotations

from fastapi import status
from .app_error import AppError


class ExternalServiceError(AppError):
	"""Generic upstream/provider failure."""
	def __init__(self, code: str, message: str | None = None, *, extra=None) -> None:
		super().__init__(code, message, status_code=status.HTTP_502_BAD_GATEWAY, extra=extra)


