import base64
import hmac
import json
import os
import secrets
import time
from hashlib import pbkdf2_hmac, sha256
from typing import Any, Dict, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.settings import get_settings
from backend.db.models import User
from backend.core.constants import Auth as AuthConst, Errors


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_json(obj: Dict[str, Any]) -> str:
    return _b64url(json.dumps(obj, separators=(",", ":"), sort_keys=True).encode("utf-8"))

def _b64url_decode(data: str) -> bytes:
    # add padding
    pad = '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + pad)

def hash_password(password: str, *, iterations: int = 100_000) -> str:
    salt = os.urandom(16)
    dk = pbkdf2_hmac(AuthConst.PBKDF2_HASH_NAME, password.encode("utf-8"), salt, iterations)
    return f"{AuthConst.PASSWORD_SCHEME_PBKDF2_SHA256}${iterations}${salt.hex()}${dk.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algo, iter_str, salt_hex, hash_hex = encoded.split("$", 3)
        if algo != AuthConst.PASSWORD_SCHEME_PBKDF2_SHA256:
            return False
        iterations = int(iter_str)
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)
        dk = pbkdf2_hmac(AuthConst.PBKDF2_HASH_NAME, password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(dk, expected)
    except Exception:
        return False


def issue_token(user_id: str, now: Optional[int] = None) -> str:
    """
    Minimal JWT (HS256) implementation without external deps.
    """
    settings = get_settings()
    secret = settings.auth_secret.encode("utf-8")
    iat = int(now or time.time())
    exp = iat + settings.auth_token_exp_minutes * 60
    header = {"alg": AuthConst.JWT_ALG_HS256, "typ": AuthConst.JWT_TYP_JWT}
    payload = {AuthConst.JWT_CLAIM_SUB: user_id, AuthConst.JWT_CLAIM_IAT: iat, AuthConst.JWT_CLAIM_EXP: exp}
    encoded_header = _b64url_json(header)
    encoded_payload = _b64url_json(payload)
    signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
    sig = hmac.new(secret, signing_input, sha256).digest()
    return f"{encoded_header}.{encoded_payload}.{_b64url(sig)}"

def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify HS256 token signature and expiry. Returns payload dict.
    Raises ValueError on failure.
    """
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError(Errors.MALFORMED_TOKEN)
        encoded_header, encoded_payload, encoded_sig = parts
        header = json.loads(_b64url_decode(encoded_header).decode("utf-8"))
        if header.get("alg") != AuthConst.JWT_ALG_HS256 or header.get("typ") != AuthConst.JWT_TYP_JWT:
            raise ValueError(Errors.MALFORMED_TOKEN)
        payload = json.loads(_b64url_decode(encoded_payload).decode("utf-8"))
        signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
        settings = get_settings()
        expected = hmac.new(settings.auth_secret.encode("utf-8"), signing_input, sha256).digest()
        provided = _b64url_decode(encoded_sig)
        if not hmac.compare_digest(expected, provided):
            raise ValueError(Errors.INVALID_CREDENTIALS)
        now = int(time.time())
        exp = int(payload.get(AuthConst.JWT_CLAIM_EXP, 0))
        if exp < now:
            raise ValueError(Errors.INVALID_CREDENTIALS)
        return payload
    except ValueError:
        raise
    except Exception:
        raise ValueError(Errors.MALFORMED_TOKEN)


class AuthService:
    def signup(
        self,
        db: Session,
        *,
        username: str,
        email: str,
        password: str,
        role: str,
        corpus_uri: str,
        chat_history_uri: Optional[str],
        account_type: Optional[str] = None,
        group_id: Optional[str] = None,
        gcp_project_id: Optional[str] = None,
        temp_bucket: Optional[str] = None,
        payment_info: Optional[Dict[str, Any]] = None,
    ) -> Tuple[User, str]:
        # Uniqueness checks
        if db.scalar(select(User).where(User.username == username)) is not None:
            raise ValueError(Errors.USERNAME_TAKEN)
        if db.scalar(select(User).where(User.email == email)) is not None:
            raise ValueError(Errors.EMAIL_TAKEN)

        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            role=role,
            corpus_uri=corpus_uri,
            chat_history_uri=chat_history_uri,
            account_type=account_type,
            group_id=group_id,
            gcp_project_id=gcp_project_id,
            temp_bucket=temp_bucket,
            payment_info=payment_info,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        token = issue_token(str(user.id))
        return user, token

    def login(self, db: Session, *, username: str, password: str) -> Tuple[User, str]:
        user = db.scalar(select(User).where(User.username == username))
        if user is None or not verify_password(password, user.password_hash):
            raise ValueError(Errors.INVALID_CREDENTIALS)
        token = issue_token(str(user.id))
        return user, token

    def verify_token(self, token: str) -> Dict[str, Any]:
        return verify_token(token)


