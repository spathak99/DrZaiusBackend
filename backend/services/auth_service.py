"""Auth service and helpers: password hashing, token issuance/verification, and user signup/login flows."""
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
from backend.db.models import User, Group, GroupMembership
from backend.core.constants import Auth as AuthConst, Errors, GroupRoles, Fields


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
    header = {AuthConst.JWT_HEADER_ALG: AuthConst.JWT_ALG_HS256, AuthConst.JWT_HEADER_TYP: AuthConst.JWT_TYP_JWT}
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
        if header.get(AuthConst.JWT_HEADER_ALG) != AuthConst.JWT_ALG_HS256 or header.get(AuthConst.JWT_HEADER_TYP) != AuthConst.JWT_TYP_JWT:
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
    """Provide signup, login, token verification, and password change operations."""
    def signup(
        self,
        db: Session,
        *,
        username: str,
        email: str,
        password: str,
        role: str,
        full_name: Optional[str],
        phone_number: Optional[str],
        age: Optional[int],
        country: Optional[str],
        avatar_uri: Optional[str],
        corpus_uri: str,
        chat_history_uri: Optional[str],
        account_type: Optional[str] = None,
        group_id: Optional[str] = None,
        gcp_project_id: Optional[str] = None,
        temp_bucket: Optional[str] = None,
        payment_info: Optional[Dict[str, Any]] = None,
    ) -> Tuple[User, str]:
        """Create a new user and return (user, access_token)."""
        # normalize email/username casing BEFORE uniqueness checks
        username = (username or "").strip().lower()
        email = (email or "").strip().lower()
        # Uniqueness checks (normalized)
        if db.scalar(select(User).where(User.username == username)) is not None:
            raise ValueError(Errors.USERNAME_TAKEN)
        if db.scalar(select(User).where(User.email == email)) is not None:
            raise ValueError(Errors.EMAIL_TAKEN)

        user = User(
            username=username,
            email=email,
            password_hash=hash_password(password),
            role=role,
            full_name=full_name,
            phone_number=phone_number,
            age=age,
            country=country,
            avatar_uri=avatar_uri,
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
        # If group plan, create a group and add creator as admin
        if (account_type or "").lower() == "group":
            group = Group(name=f"{full_name or username}'s Group", description=None, created_by=user.id)
            db.add(group)
            db.commit()
            db.refresh(group)
            # optional convenience pointer
            user.group_id = group.id
            db.add(user)
            db.commit()
            # membership as admin (idempotent insert)
            gm = GroupMembership(group_id=group.id, user_id=user.id, role=GroupRoles.ADMIN)
            db.add(gm)
            db.commit()
        token = issue_token(str(user.id))
        return user, token

    def login(self, db: Session, *, username: str, password: str) -> Tuple[User, str]:
        """Authenticate by username or email and return (user, access_token)."""
        # normalize username/email for lookup
        username = (username or "").strip().lower()
        user = db.scalar(select(User).where(User.username == username))
        if user is None:
            # fallback: allow login via email as well
            user = db.scalar(select(User).where(User.email == username))
        if user is None or not verify_password(password, user.password_hash):
            raise ValueError(Errors.INVALID_CREDENTIALS)
        token = issue_token(str(user.id))
        return user, token

    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify a bearer token and return its payload or raise ValueError."""
        return verify_token(token)

    def change_password(
        self,
        db: Session,
        *,
        user: User,
        current_password: str,
        new_password: str,
    ) -> None:
        """Change the user's password after verifying the current password."""
        from backend.core.constants import Errors as Err

        if not verify_password(current_password, user.password_hash):
            raise ValueError(Err.INCORRECT_PASSWORD)
        user.password_hash = hash_password(new_password)
        db.commit()
        db.refresh(user)


