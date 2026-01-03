from __future__ import annotations

from fastapi import status
from .app_error import AppError


class ConflictError(AppError):
	def __init__(self, code: str, message: str | None = None, *, extra=None) -> None:
		super().__init__(code, message, status_code=status.HTTP_409_CONFLICT, extra=extra)


