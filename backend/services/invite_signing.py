"""Invite signing utilities: HMAC-sign compact tokens for deep links."""
import base64
import hashlib
import hmac
import json
from typing import Any, Dict, Optional

from backend.core.settings import get_settings
from backend.core.constants import Errors


def _b64url_encode(data: bytes) -> str:
    """Base64url-encode bytes without padding."""
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")


def _b64url_decode(data: str) -> bytes:
    """Base64url-decode a string, adding required padding."""
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + padding).encode("utf-8"))


def sign_invite(payload: Dict[str, Any], secret_override: Optional[str] = None) -> str:
    """
    Create a compact token: base64url(json).base64url(hmac_sha256)
    Payload should include: invitationId, role ('recipient'|'caregiver'), and optionally recipientId/caregiverId.
    """
    secret = (secret_override or get_settings().invite_signing_secret).encode("utf-8")
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    sig = hmac.new(secret, body, hashlib.sha256).digest()
    return f"{_b64url_encode(body)}.{_b64url_encode(sig)}"


def verify_invite(token: str, secret_override: Optional[str] = None) -> Dict[str, Any]:
    """
    Verify token integrity and return decoded payload.
    Raises ValueError if invalid.
    """
    try:
        body_b64, sig_b64 = token.split(".", 1)
    except ValueError as e:
        raise ValueError(Errors.MALFORMED_TOKEN) from e
    body = _b64url_decode(body_b64)
    sig = _b64url_decode(sig_b64)
    secret = (secret_override or get_settings().invite_signing_secret).encode("utf-8")
    expected = hmac.new(secret, body, hashlib.sha256).digest()
    if not hmac.compare_digest(sig, expected):
        raise ValueError(Errors.INVALID_TOKEN)
    try:
        data = json.loads(body.decode("utf-8"))
    except Exception as e:
        raise ValueError(Errors.INVALID_PAYLOAD) from e
    return data


