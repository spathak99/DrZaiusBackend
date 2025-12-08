from typing import Any, Dict
from fastapi import APIRouter
from backend.core.constants import Tags, Summaries, Messages, Routes, Keys


router = APIRouter(tags=[Tags.OPS])


@router.get(Routes.HEALTHZ, summary=Summaries.HEALTHZ)
async def healthz() -> Dict[str, Any]:
    return {Keys.STATUS: Messages.OK}


@router.get(Routes.READYZ, summary=Summaries.READYZ)
async def readyz() -> Dict[str, Any]:
    return {Keys.STATUS: Messages.READY}


