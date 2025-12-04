from typing import Any, Dict
from fastapi import APIRouter
from backend.core.constants import Tags, Summaries, Messages


router = APIRouter(tags=[Tags.OPS])


@router.get("/healthz", summary=Summaries.HEALTHZ)
async def healthz() -> Dict[str, Any]:
    return {"status": Messages.OK}


@router.get("/readyz", summary=Summaries.READYZ)
async def readyz() -> Dict[str, Any]:
    return {"status": Messages.READY}


