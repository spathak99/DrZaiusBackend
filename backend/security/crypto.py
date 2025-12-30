from __future__ import annotations

from typing import Tuple


class AeadCipher:
	"""
	Interface for AEAD operations. AES-GCM implementation will be added later.
	For now, provide a no-op cipher so wiring can proceed safely.
	"""

	def encrypt(self, key: bytes, plaintext: bytes, aad: bytes = b"") -> Tuple[bytes, bytes, bytes]:
		"""
		Returns (nonce, ciphertext, tag). No-op: echoes plaintext and empty tag.
		"""
		nonce = b""
		tag = b""
		return nonce, plaintext, tag

	def decrypt(self, key: bytes, nonce: bytes, ciphertext: bytes, tag: bytes, aad: bytes = b"") -> bytes:
		"""
		No-op: returns ciphertext as-is.
		"""
		return ciphertext


def get_cipher() -> AeadCipher:
	return AeadCipher()


