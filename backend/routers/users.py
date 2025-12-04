from typing import Any, Dict
from fastapi import APIRouter, Body, status
from backend.core.constants import Prefix, Tags
from backend.schemas import UserCreate, UserUpdate


router = APIRouter(prefix=Prefix.USERS, tags=[Tags.USERS])


@router.get("", summary="Get a list of users")
async def list_users() -> Dict[str, Any]:
    return {"items": []}


@router.post("", status_code=status.HTTP_201_CREATED, summary="Create a user (admin)")
async def create_user(payload: UserCreate = Body(default=None)) -> Dict[str, Any]:
    return {"message": "user created", "data": payload.model_dump()}


@router.get("/{id}", summary="Get a specific user by ID")
async def get_user(id: str) -> Dict[str, Any]:
    return {"id": id}


@router.put("/{id}", summary="Update user details")
async def update_user(id: str, payload: UserUpdate = Body(default=None)) -> Dict[str, Any]:
    return {"message": "user updated", "id": id, "data": payload.model_dump(exclude_none=True)}


@router.delete(
    "/{id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete user (admin)"
)
async def delete_user(id: str) -> None:
    return


