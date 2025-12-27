from typing import Any, Dict
from fastapi import APIRouter, Body, status
from backend.core.constants import Prefix, Tags, Summaries, Routes, Fields
from backend.schemas import SecurityPolicyCreate, SecurityPolicyUpdate, KeyGenerateRequest
from backend.services import SecurityService


keys_router = APIRouter(prefix=Prefix.SECURITY_KEYS, tags=[Tags.SECURITY])
policies_router = APIRouter(prefix=Prefix.SECURITY_POLICIES, tags=[Tags.SECURITY])
service = SecurityService()


@keys_router.post(Routes.ROOT, status_code=status.HTTP_201_CREATED, summary=Summaries.KEY_GENERATE)
async def generate_key_pair(payload: KeyGenerateRequest = Body(default=None)) -> Dict[str, Any]:
    return service.generate_key_pair(payload.model_dump(exclude_none=True))


@keys_router.get(Routes.ID, summary=Summaries.KEY_GET)
async def get_key(id: str) -> Dict[str, Any]:
    return {Fields.ID: id}


@policies_router.post(Routes.ROOT, status_code=status.HTTP_201_CREATED, summary=Summaries.POLICY_CREATE)
async def create_policy(payload: SecurityPolicyCreate = Body(default=None)) -> Dict[str, Any]:
    return service.create_policy(payload.model_dump(exclude_none=True))


@policies_router.get(Routes.ID, summary=Summaries.POLICY_GET)
async def get_policy(id: str) -> Dict[str, Any]:
    return {Fields.ID: id}


@policies_router.put(Routes.ID, summary=Summaries.POLICY_UPDATE)
async def update_policy(id: str, payload: SecurityPolicyUpdate = Body(default=None)) -> Dict[str, Any]:
    return service.update_policy(id, payload.model_dump(exclude_none=True))


@policies_router.delete(Routes.ID, status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.POLICY_DELETE)
async def delete_policy(id: str) -> None:
    service.delete_policy(id)
    return


