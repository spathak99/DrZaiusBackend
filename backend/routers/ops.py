from typing import Any, Dict
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import text
from sqlalchemy.orm import Session
from backend.core.constants import Tags, Summaries, Messages, Routes, Keys, Errors
from backend.db.database import get_db


router = APIRouter(tags=[Tags.OPS])


@router.get(Routes.HEALTHZ, summary=Summaries.HEALTHZ)
async def healthz() -> Dict[str, Any]:
    return {Keys.STATUS: Messages.OK}


@router.get(Routes.READYZ, summary=Summaries.READYZ)
async def readyz(db: Session = Depends(get_db)) -> Dict[str, Any]:
    try:
        db.execute(text("SELECT 1"))
        return {Keys.STATUS: Messages.READY}
    except Exception:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=Errors.DB_UNAVAILABLE)


