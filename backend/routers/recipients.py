from typing import Any, Dict, List
from fastapi import APIRouter, Body, status, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.core.constants import Prefix, Tags, Summaries, Messages, Routes, Keys, Fields
from backend.routers.deps import get_current_user
from backend.db.database import get_db
from backend.db.models import User, RecipientCaregiverAccess


router = APIRouter(prefix=Prefix.RECIPIENTS, tags=[Tags.RECIPIENTS], dependencies=[Depends(get_current_user)])


@router.get(Routes.ROOT, summary=Summaries.RECIPIENTS_LIST)
async def list_recipients(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Dict[str, Any]:
    items: List[Dict[str, Any]] = []
    # If the current user is a caregiver, list recipients they have access to
    if current_user.role == "caregiver":
        rows = db.scalars(select(RecipientCaregiverAccess).where(RecipientCaregiverAccess.caregiver_id == current_user.id)).all()
        recipient_ids = [r.recipient_id for r in rows if r.recipient_id is not None]
        if recipient_ids:
            recipients = db.scalars(select(User).where(User.id.in_(recipient_ids))).all()
            items = [{Fields.ID: u.id, Fields.FULL_NAME: u.full_name or u.username} for u in recipients]
    else:
        # Current user is a recipient; include self as the only recipient
        items = [{Fields.ID: current_user.id, Fields.FULL_NAME: current_user.full_name or current_user.username}]
    return {Keys.ITEMS: items}


@router.post(Routes.ROOT, status_code=status.HTTP_201_CREATED, summary=Summaries.RECIPIENT_CREATE)
async def create_recipient(payload: Dict[str, Any] = Body(default=None)) -> Dict[str, Any]:
    return {Keys.MESSAGE: Messages.RECIPIENT_CREATED, Keys.DATA: payload}


@router.get(Routes.ID, summary=Summaries.RECIPIENT_GET)
async def get_recipient(id: str) -> Dict[str, Any]:
    return {Fields.ID: id}


@router.put(Routes.ID, summary=Summaries.RECIPIENT_UPDATE)
async def update_recipient(id: str, payload: Dict[str, Any] = Body(default=None)) -> Dict[str, Any]:
    return {Keys.MESSAGE: Messages.RECIPIENT_UPDATED, Fields.ID: id, Keys.DATA: payload}


@router.delete(Routes.ID, status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.RECIPIENT_DELETE)
async def delete_recipient(id: str) -> None:
    return


