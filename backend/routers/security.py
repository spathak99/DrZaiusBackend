from typing import Any, Dict
from fastapi import APIRouter, Body, status
from backend.core.constants import Prefix, Tags
from backend.schemas import SecurityPolicyCreate, SecurityPolicyUpdate, KeyGenerateRequest
from backend.services import SecurityService


keys_router = APIRouter(prefix=Prefix.SECURITY_KEYS, tags=[Tags.SECURITY])
policies_router = APIRouter(prefix=Prefix.SECURITY_POLICIES, tags=[Tags.SECURITY])
service = SecurityService()


@keys_router.post("", status_code=status.HTTP_201_CREATED, summary="Generate a new encryption key pair (admin only)")
async def generate_key_pair(payload: KeyGenerateRequest = Body(default=None)) -> Dict[str, Any]:
    return service.generate_key_pair(payload.model_dump(exclude_none=True))


@keys_router.get("/{id}", summary="Get a specific encryption key (admin only)")
async def get_key(id: str) -> Dict[str, Any]:
    return {"id": id}


@policies_router.post("", status_code=status.HTTP_201_CREATED, summary="Create a new security policy (admin only)")
async def create_policy(payload: SecurityPolicyCreate = Body(default=None)) -> Dict[str, Any]:
    return service.create_policy(payload.model_dump(exclude_none=True))


@policies_router.get("/{id}", summary="Get a specific security policy (admin only)")
async def get_policy(id: str) -> Dict[str, Any]:
    return {"id": id}


@policies_router.put("/{id}", summary="Update a security policy (admin only)")
async def update_policy(id: str, payload: SecurityPolicyUpdate = Body(default=None)) -> Dict[str, Any]:
    return service.update_policy(id, payload.model_dump(exclude_none=True))


@policies_router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a security policy (admin only)",
)
async def delete_policy(id: str) -> None:
    service.delete_policy(id)
    return


