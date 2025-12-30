from __future__ import annotations

from typing import Optional, Protocol
from backend.core.settings import get_settings


class KeyProvider(Protocol):
	def get_dek(self) -> bytes: ...
	def key_id(self) -> str: ...


class EnvKeyProvider:
	def __init__(self) -> None:
		self._settings = get_settings()

	def get_dek(self) -> bytes:
		# Expect base64-encoded DEK in settings; if missing, return empty to force no-op
		import base64
		b64 = (self._settings.encryption_env_key_b64 or "").strip()
		return base64.b64decode(b64) if b64 else b""

	def key_id(self) -> str:
		return (self._settings.encryption_key_id or "").strip()


class SecretManagerKeyProvider:
	def __init__(self) -> None:
		self._settings = get_settings()

	def get_dek(self) -> bytes:
		# Stub: integrate GCP Secret Manager later
		# For now return empty to indicate unavailable
		return b""

	def key_id(self) -> str:
		return (self._settings.encryption_key_id or "").strip()


class KmsKeyProvider:
	def __init__(self) -> None:
		self._settings = get_settings()

	def get_dek(self) -> bytes:
		# Stub: integrate KMS wrap/unwrap later
		return b""

	def key_id(self) -> str:
		return (self._settings.encryption_key_id or "").strip()


def get_key_provider() -> KeyProvider:
	settings = get_settings()
	provider = (settings.encryption_provider or "env").lower()
	if provider == "secret_manager":
		return SecretManagerKeyProvider()
	if provider == "kms":
		return KmsKeyProvider()
	return EnvKeyProvider()


