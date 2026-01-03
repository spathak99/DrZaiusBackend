from __future__ import annotations

from fastapi import status
from backend.core.constants import Errors
from .app_error import AppError


class NotFoundError(AppError):
	def __init__(self, code: str = Errors.USER_NOT_FOUND, message: str | None = None, *, extra=None) -> None:
		super().__init__(code, message, status_code=status.HTTP_404_NOT_FOUND, extra=extra)


