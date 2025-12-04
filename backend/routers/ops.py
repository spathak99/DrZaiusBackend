from typing import Any, Dict
from fastapi import APIRouter
from backend.core.constants import Tags


router = APIRouter(tags=[Tags.OPS])


@router.get("/healthz", summary="Liveness probe")
async def healthz() -> Dict[str, Any]:
    return {"status": "ok"}


@router.get("/readyz", summary="Readiness probe")
async def readyz() -> Dict[str, Any]:
    return {"status": "ready"}


