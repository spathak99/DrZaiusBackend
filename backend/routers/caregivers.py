from typing import Any, Dict
from fastapi import APIRouter, Body, status, Depends
from backend.core.constants import Prefix, Tags, Summaries, Messages, Routes, Keys, Fields
from backend.routers.deps import get_current_user


router = APIRouter(prefix=Prefix.CAREGIVERS, tags=[Tags.CAREGIVERS], dependencies=[Depends(get_current_user)])


@router.get(Routes.ROOT, summary=Summaries.CAREGIVERS_LIST)
async def list_caregivers() -> Dict[str, Any]:
    return {Keys.ITEMS: []}


@router.post(Routes.ROOT, status_code=status.HTTP_201_CREATED, summary=Summaries.CAREGIVER_CREATE)
async def create_caregiver(payload: Dict[str, Any] = Body(default=None)) -> Dict[str, Any]:
    return {Keys.MESSAGE: Messages.CAREGIVER_CREATED, Keys.DATA: payload}


@router.get(Routes.ID, summary=Summaries.CAREGIVER_GET)
async def get_caregiver(id: str) -> Dict[str, Any]:
    return {Fields.ID: id}


@router.put(Routes.ID, summary=Summaries.CAREGIVER_UPDATE)
async def update_caregiver(id: str, payload: Dict[str, Any] = Body(default=None)) -> Dict[str, Any]:
    return {Keys.MESSAGE: Messages.CAREGIVER_UPDATED, Fields.ID: id, Keys.DATA: payload}


@router.delete(Routes.ID, status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.CAREGIVER_DELETE)
async def delete_caregiver(id: str) -> None:
    return


