from __future__ import annotations

from fastapi import status
from backend.core.constants import Errors
from .app_error import AppError


class ForbiddenError(AppError):
	def __init__(self, message: str | None = None, *, extra=None) -> None:
		super().__init__(Errors.FORBIDDEN, message, status_code=status.HTTP_403_FORBIDDEN, extra=extra)


