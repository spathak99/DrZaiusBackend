from typing import Any, Dict
from fastapi import APIRouter, Body, status
from backend.core.constants import Prefix, Tags


router = APIRouter(prefix=Prefix.RECIPIENTS, tags=[Tags.RECIPIENTS])


@router.get("", summary="Get a list of all recipients")
async def list_recipients() -> Dict[str, Any]:
    return {"items": []}


@router.post("", status_code=status.HTTP_201_CREATED, summary="Register a new recipient (admin only)")
async def create_recipient(payload: Dict[str, Any] = Body(default=None)) -> Dict[str, Any]:
    return {"message": "recipient created", "data": payload}


@router.get("/{id}", summary="Get a specific recipient's details")
async def get_recipient(id: str) -> Dict[str, Any]:
    return {"id": id}


@router.put("/{id}", summary="Update a recipient's details")
async def update_recipient(id: str, payload: Dict[str, Any] = Body(default=None)) -> Dict[str, Any]:
    return {"message": "recipient updated", "id": id, "data": payload}


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a recipient")
async def delete_recipient(id: str) -> None:
    return


