from __future__ import annotations

from .external_service_error import ExternalServiceError
from backend.core.constants import ErrorCodes


class DlpError(ExternalServiceError):
	def __init__(self, message: str | None = None, *, extra=None) -> None:
		super().__init__(ErrorCodes.DLP_ERROR, message, extra=extra)


