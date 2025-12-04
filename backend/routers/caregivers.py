from typing import Any, Dict
from fastapi import APIRouter, Body, status
from backend.core.constants import Prefix, Tags, Summaries, Messages


router = APIRouter(prefix=Prefix.CAREGIVERS, tags=[Tags.CAREGIVERS])


@router.get("", summary=Summaries.CAREGIVERS_LIST)
async def list_caregivers() -> Dict[str, Any]:
    return {"items": []}


@router.post("", status_code=status.HTTP_201_CREATED, summary=Summaries.CAREGIVER_CREATE)
async def create_caregiver(payload: Dict[str, Any] = Body(default=None)) -> Dict[str, Any]:
    return {"message": Messages.CAREGIVER_CREATED, "data": payload}


@router.get("/{id}", summary=Summaries.CAREGIVER_GET)
async def get_caregiver(id: str) -> Dict[str, Any]:
    return {"id": id}


@router.put("/{id}", summary=Summaries.CAREGIVER_UPDATE)
async def update_caregiver(id: str, payload: Dict[str, Any] = Body(default=None)) -> Dict[str, Any]:
    return {"message": Messages.CAREGIVER_UPDATED, "id": id, "data": payload}


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.CAREGIVER_DELETE)
async def delete_caregiver(id: str) -> None:
    return


