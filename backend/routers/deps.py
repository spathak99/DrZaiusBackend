from typing import Optional
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.core.constants import Errors, Auth as AuthConst, Messages
from backend.db.database import get_db
from backend.db.models import User
from backend.services.auth_service import AuthService


auth_service = AuthService()


def get_current_user(
    authorization: Optional[str] = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    if not authorization:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Errors.UNAUTHORIZED)
    scheme, _, token = authorization.partition(" ")
    if not token or scheme.lower() != Messages.TOKEN_TYPE_BEARER:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Errors.UNAUTHORIZED)
    try:
        payload = auth_service.verify_token(token)
        user_id = payload.get(AuthConst.JWT_CLAIM_SUB)
        if not user_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Errors.UNAUTHORIZED)
        # Coerce to UUID for safety
        try:
            user_uuid = UUID(user_id)
        except Exception:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Errors.UNAUTHORIZED)
        user = db.scalar(select(User).where(User.id == user_uuid))
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Errors.UNAUTHORIZED)
        return user
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=Errors.INVALID_CREDENTIALS)


