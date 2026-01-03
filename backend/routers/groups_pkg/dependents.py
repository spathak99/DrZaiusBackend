from __future__ import annotations

from typing import Any, Dict
from fastapi import APIRouter, Body, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session

from backend.core.constants import Routes, Keys, Fields, Summaries, Headers, Pagination as PaginationConsts
from backend.db.database import get_db
from backend.routers.deps import get_current_user, get_dependents_service
from backend.db.models import User
from backend.utils.pagination import clamp_limit_offset
from backend.routers.http_errors import status_for_error
from backend.schemas.dependents import DependentCreate, DependentItem, DependentsEnvelope, DependentConvertRequest, DependentConvertResponse
from backend.services.dependents_service import DependentsService

router = APIRouter()


@router.post(Routes.ID + "/dependents", summary="Create dependent", response_model=DependentItem)
async def create_dependent(id: str, request: Request, payload: DependentCreate = Body(default=None), current_user: User = Depends(get_current_user), db: Session = Depends(get_db), svc: DependentsService = Depends(get_dependents_service)) -> Dict[str, Any]:
	try:
		data = svc.create(db, group_id=id, actor_id=str(current_user.id), full_name=payload.full_name, dob=payload.dob, email=str(payload.email) if payload.email else None)
	except ValueError as e:
		detail = str(e)
		raise HTTPException(status_code=status_for_error(detail), detail=detail)
	return DependentItem(**{"id": data.get(Fields.ID), "full_name": data.get(Fields.FULL_NAME), "dob": data.get(Keys.DOB), "email": data.get(Fields.EMAIL), "guardian_user_id": data.get(Keys.GUARDIAN_USER_ID)})


@router.get(Routes.ID + "/dependents", summary="List dependents", response_model=DependentsEnvelope)
async def list_dependents(id: str, response: Response, limit: int = PaginationConsts.DEFAULT_LIMIT, offset: int = PaginationConsts.DEFAULT_OFFSET, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), svc: DependentsService = Depends(get_dependents_service)) -> Dict[str, Any]:
	limit, offset = clamp_limit_offset(limit, offset, max_limit=PaginationConsts.MAX_LIMIT)
	try:
		result = svc.list(db, group_id=id, actor_id=str(current_user.id), limit=limit, offset=offset)
	except ValueError as e:
		detail = str(e)
		raise HTTPException(status_code=status_for_error(detail), detail=detail)
	items = [DependentItem(**it) for it in result.get(Keys.ITEMS, [])]
	response.headers[Headers.TOTAL_COUNT] = str(result.get(Keys.TOTAL, len(items)))
	return {"items": items}


@router.delete(Routes.ID + "/dependents" + Routes.USER_ID, status_code=status.HTTP_204_NO_CONTENT, summary="Delete dependent")
async def delete_dependent(id: str, userId: str, request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), svc: DependentsService = Depends(get_dependents_service)) -> None:
	try:
		svc.delete(db, group_id=id, actor_id=str(current_user.id), dependent_id=userId)
	except ValueError as e:
		detail = str(e)
		raise HTTPException(status_code=status_for_error(detail), detail=detail)
	return


@router.post(Routes.ID + "/dependents" + Routes.USER_ID + "/convert", summary="Convert dependent to account", response_model=DependentConvertResponse)
async def convert_dependent(id: str, userId: str, request: Request, payload: DependentConvertRequest = Body(default=None), current_user: User = Depends(get_current_user), db: Session = Depends(get_db), svc: DependentsService = Depends(get_dependents_service)) -> Dict[str, Any]:
	try:
		data = svc.convert_to_account(db, group_id=id, actor_id=str(current_user.id), dependent_id=userId, email=(str(payload.email) if payload and payload.email else None))
	except ValueError as e:
		detail = str(e)
		raise HTTPException(status_code=status_for_error(detail), detail=detail)
	return DependentConvertResponse(message=data.get(Keys.MESSAGE), userId=data.get(Keys.USER_ID))


