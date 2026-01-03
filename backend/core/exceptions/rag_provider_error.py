from __future__ import annotations

from .external_service_error import ExternalServiceError
from backend.core.constants import ErrorCodes


class RagProviderError(ExternalServiceError):
	def __init__(self, message: str | None = None, *, extra=None) -> None:
		super().__init__(ErrorCodes.RAG_PROVIDER_ERROR, message, extra=extra)


