from __future__ import annotations

from typing import Any, Dict
from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.constants import Prefix, Tags, Routes, Summaries, Errors, Keys
from backend.db.database import get_db
from backend.routers.deps import get_current_user
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

router = APIRouter(tags=[Tags.GROUPS])


def _raise(detail: str) -> None:
	code = status.HTTP_400_BAD_REQUEST
	if detail == Errors.FORBIDDEN:
		code = status.HTTP_403_FORBIDDEN
	if detail in (Errors.PAYMENT_CODE_NOT_FOUND,):
		code = status.HTTP_404_NOT_FOUND
	if detail in (Errors.PAYMENT_CODE_EXPIRED, Errors.PAYMENT_CODE_REDEEMED_ALREADY):
		code = status.HTTP_409_CONFLICT
	raise HTTPException(status_code=code, detail=detail)


@router.post(Prefix.GROUPS + Routes.ID + "/payments/codes", response_model=CodeCreateResponse, summary=Summaries.PAYMENT_CODE_CREATE)
async def create_code(
	id: str,
	payload: CodeCreateRequest = Body(default=None),
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> Dict[str, Any]:
	svc = PaymentCodesService()
	try:
		data = svc.create_code(db, group_id=id, actor_id=str(current_user.id), ttl_minutes=payload.ttl_minutes or 0)
	except ValueError as e:
		_raise(str(e))
	return {"code": data.get(Keys.CODE), "status": data.get(Keys.STATUS), "expires_at": data.get("expires_at")}


@router.get(Prefix.GROUPS + Routes.ID + "/payments/codes", response_model=CodesListEnvelope, summary=Summaries.PAYMENT_CODES_LIST)
async def list_codes(
	id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> Dict[str, Any]:
	svc = PaymentCodesService()
	try:
		rows = svc.list_codes(db, group_id=id, actor_id=str(current_user.id))
	except ValueError as e:
		_raise(str(e))
	items = [CodeListItem(code=r.get(Keys.CODE), status=r.get(Keys.STATUS), expires_at=r.get(Keys.EXPIRES_AT), redeemed_by=r.get(Keys.REDEEMED_BY)) for r in rows]
	return {"items": items}


@router.post(Prefix.GROUPS + Routes.ID + "/payments/codes/{code}/void", summary=Summaries.PAYMENT_CODE_VOID, status_code=status.HTTP_204_NO_CONTENT)
async def void_code(
	id: str, code: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
) -> None:
	svc = PaymentCodesService()
	try:
		svc.void_code(db, group_id=id, actor_id=str(current_user.id), code=code)
	except ValueError as e:
		_raise(str(e))
	return


@router.post("/payments/redeem", response_model=RedeemResponse, summary=Summaries.PAYMENT_CODE_REDEEM)
async def redeem_code(
	payload: RedeemRequest = Body(default=None),
	current_user: User = Depends(get_current_user),
	db: Session = Depends(get_db),
) -> Dict[str, Any]:
	svc = PaymentCodesService()
	try:
		data = svc.redeem(db, code=payload.code, user_id=str(current_user.id))
	except ValueError as e:
		_raise(str(e))
	return {"message": data.get(Keys.MESSAGE), "code": data.get(Keys.CODE)}


