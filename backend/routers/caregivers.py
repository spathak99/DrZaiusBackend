from typing import Any, Dict
from fastapi import APIRouter, Body, status
from backend.core.constants import Prefix, Tags, Summaries, Messages, Routes


router = APIRouter(prefix=Prefix.CAREGIVERS, tags=[Tags.CAREGIVERS])


@router.get(Routes.ROOT, summary=Summaries.CAREGIVERS_LIST)
async def list_caregivers() -> Dict[str, Any]:
    return {"items": []}


@router.post(Routes.ROOT, status_code=status.HTTP_201_CREATED, summary=Summaries.CAREGIVER_CREATE)
async def create_caregiver(payload: Dict[str, Any] = Body(default=None)) -> Dict[str, Any]:
    return {"message": Messages.CAREGIVER_CREATED, "data": payload}


@router.get(Routes.ID, summary=Summaries.CAREGIVER_GET)
async def get_caregiver(id: str) -> Dict[str, Any]:
    return {"id": id}


@router.put(Routes.ID, summary=Summaries.CAREGIVER_UPDATE)
async def update_caregiver(id: str, payload: Dict[str, Any] = Body(default=None)) -> Dict[str, Any]:
    return {"message": Messages.CAREGIVER_UPDATED, "id": id, "data": payload}


@router.delete(Routes.ID, status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.CAREGIVER_DELETE)
async def delete_caregiver(id: str) -> None:
    return


