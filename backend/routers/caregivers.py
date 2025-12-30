from typing import Any, Dict, List
from fastapi import APIRouter, Body, status, Depends, Response
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.core.constants import Prefix, Tags, Summaries, Messages, Routes, Keys, Fields, Roles, Headers
from backend.routers.deps import get_current_user
from backend.db.database import get_db
from backend.db.models import User, RecipientCaregiverAccess


router = APIRouter(prefix=Prefix.CAREGIVERS, tags=[Tags.CAREGIVERS], dependencies=[Depends(get_current_user)])


@router.get(Routes.ROOT, summary=Summaries.CAREGIVERS_LIST)
async def list_caregivers(
    response: Response,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    # Always list caregivers that have access to this user as recipient,
    # regardless of the user's global role label.
    rows = db.scalars(
        select(RecipientCaregiverAccess).where(RecipientCaregiverAccess.recipient_id == current_user.id)
    ).all()
    caregiver_ids = [r.caregiver_id for r in rows if r.caregiver_id is not None]
    if caregiver_ids:
        caregivers = db.scalars(select(User).where(User.id.in_(caregiver_ids))).all()
        items: List[Dict[str, Any]] = [
            {Fields.ID: u.id, Fields.FULL_NAME: u.full_name or u.username, Fields.ROLE: u.role} for u in caregivers
        ]
        response.headers[Headers.TOTAL_COUNT] = str(len(items))
        return {Keys.ITEMS: items}
    # If user has no caregivers assigned and is a caregiver themselves, don't list self
    if current_user.role == Roles.CAREGIVER:
        response.headers[Headers.TOTAL_COUNT] = "0"
        return {Keys.ITEMS: []}
    # Fallback: if user is a recipient with no caregivers yet, return empty
    response.headers[Headers.TOTAL_COUNT] = "0"
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


