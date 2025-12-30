from __future__ import annotations

from typing import Any, Dict
from fastapi import APIRouter, Body, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session

from backend.core.constants import Prefix, Tags, Routes, Summaries, Errors, Keys, Headers
from backend.db.database import get_db
from backend.routers.deps import get_current_user, get_payment_codes_service
from backend.db.models import User
from backend.services.payment_codes_service import PaymentCodesService
from backend.schemas.payments import (
	CodeCreateRequest,
	CodeCreateResponse,
	CodesListEnvelope,
	RedeemRequest,
	RedeemResponse,
	CodeListItem,
)
from backend.routers.http_errors import status_for_error
from backend.utils.pagination import clamp_limit_offset

router = APIRouter(tags=[Tags.GROUPS])


@router.post(Prefix.GROUPS + Routes.ID + Routes.PAYMENTS + Routes.CODES, response_model=CodeCreateResponse, summary=Summaries.PAYMENT_CODE_CREATE)
async def create_code(
	id: str,
	payload: CodeCreateRequest = Body(default=None),
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
	payment_codes_service: PaymentCodesService = Depends(get_payment_codes_service),
) -> Dict[str, Any]:
	try:
		data = payment_codes_service.create_code(db, group_id=id, actor_id=str(current_user.id), ttl_minutes=payload.ttl_minutes or 0)
	except ValueError as e:
		detail = str(e)
		raise HTTPException(status_code=status_for_error(detail), detail=detail)
	return {"code": data.get(Keys.CODE), "status": data.get(Keys.STATUS), "expires_at": data.get("expires_at")}


@router.get(Prefix.GROUPS + Routes.ID + Routes.PAYMENTS + Routes.CODES, response_model=CodesListEnvelope, summary=Summaries.PAYMENT_CODES_LIST)
async def list_codes(
	id: str,
	response: Response,
	limit: int = 50,
	offset: int = 0,
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
	payment_codes_service: PaymentCodesService = Depends(get_payment_codes_service),
) -> Dict[str, Any]:
	limit, offset = clamp_limit_offset(limit, offset, max_limit=100)
	try:
		result = payment_codes_service.list_codes(db, group_id=id, actor_id=str(current_user.id), limit=limit, offset=offset)
	except ValueError as e:
		detail = str(e)
		raise HTTPException(status_code=status_for_error(detail), detail=detail)
	items = [CodeListItem(code=r.get(Keys.CODE), status=r.get(Keys.STATUS), expires_at=r.get(Keys.EXPIRES_AT), redeemed_by=r.get(Keys.REDEEMED_BY)) for r in result[Keys.ITEMS]]
	response.headers[Headers.TOTAL_COUNT] = str(result.get(Keys.TOTAL, len(items)))
	return {"items": items}


@router.post(Prefix.GROUPS + Routes.ID + Routes.PAYMENTS + Routes.CODES + Routes.CODE + Routes.VOID, summary=Summaries.PAYMENT_CODE_VOID, status_code=status.HTTP_204_NO_CONTENT)
async def void_code(
	id: str, code: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db), payment_codes_service: PaymentCodesService = Depends(get_payment_codes_service)
) -> None:
	try:
		payment_codes_service.void_code(db, group_id=id, actor_id=str(current_user.id), code=code)
	except ValueError as e:
		detail = str(e)
		raise HTTPException(status_code=status_for_error(detail), detail=detail)
	return


@router.post(Routes.PAYMENTS + Routes.REDEEM, response_model=RedeemResponse, summary=Summaries.PAYMENT_CODE_REDEEM)
async def redeem_code(
	payload: RedeemRequest = Body(default=None),
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
	payment_codes_service: PaymentCodesService = Depends(get_payment_codes_service),
) -> Dict[str, Any]:
	try:
		data = payment_codes_service.redeem(db, code=payload.code, user_id=str(current_user.id))
	except ValueError as e:
		detail = str(e)
		raise HTTPException(status_code=status_for_error(detail), detail=detail)
	return {"message": data.get(Keys.MESSAGE), "code": data.get(Keys.CODE)}


