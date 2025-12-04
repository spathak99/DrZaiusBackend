from typing import Any, Dict
from fastapi import APIRouter, Body, status
from backend.core.constants import Prefix, Tags


router = APIRouter(prefix=Prefix.CAREGIVERS, tags=[Tags.CAREGIVERS])


@router.get("", summary="Get a list of all caregivers")
async def list_caregivers() -> Dict[str, Any]:
    return {"items": []}


@router.post("", status_code=status.HTTP_201_CREATED, summary="Register a new caregiver")
async def create_caregiver(payload: Dict[str, Any] = Body(default=None)) -> Dict[str, Any]:
    return {"message": "caregiver created", "data": payload}


@router.get("/{id}", summary="Get a specific caregiver's details")
async def get_caregiver(id: str) -> Dict[str, Any]:
    return {"id": id}


@router.put("/{id}", summary="Update a caregiver's details")
async def update_caregiver(id: str, payload: Dict[str, Any] = Body(default=None)) -> Dict[str, Any]:
    return {"message": "caregiver updated", "id": id, "data": payload}


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a user as caregiver",
)
async def delete_caregiver(id: str) -> None:
    return


