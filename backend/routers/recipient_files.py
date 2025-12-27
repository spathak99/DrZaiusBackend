from typing import Any, Dict
from fastapi import APIRouter, status, Depends, HTTPException, UploadFile, File
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.core.constants import Prefix, Tags, Summaries, Messages, Routes, Keys, Errors
from backend.db.database import get_db
from backend.db.models import User, RecipientCaregiverAccess
from backend.services import DocsService
from backend.routers.deps import get_current_user


router = APIRouter(prefix=Prefix.RECIPIENT_FILES, tags=[Tags.RECIPIENT_DATA], dependencies=[Depends(get_current_user)])
docs = DocsService()

def _assert_can_access_recipient(db: Session, recipient_id: str, current_user: User) -> None:
    # Allow self
    if str(current_user.id) == recipient_id:
        return
    # Otherwise require caregiver access row
    allowed = db.scalar(
        select(RecipientCaregiverAccess).where(
            RecipientCaregiverAccess.recipient_id == recipient_id,
            RecipientCaregiverAccess.caregiver_id == current_user.id,
        )
    )
    if not allowed:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=Errors.FORBIDDEN)

@router.post(Routes.ROOT, status_code=status.HTTP_201_CREATED, summary=Summaries.FILE_UPLOAD)
async def upload_recipient_file(
    id: str, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    user = db.scalar(select(User).where(User.id == id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Errors.RECIPIENT_NOT_FOUND)
    _assert_can_access_recipient(db, id, current_user)
    content = await file.read()
    created = docs.upload_doc(
        corpus_uri=user.corpus_uri, file_name=file.filename, content_type=file.content_type, content=content
    )
    return {Keys.MESSAGE: Messages.FILE_UPLOADED, Keys.RECIPIENT_ID: id, Keys.DATA: created}


@router.get(Routes.ROOT, summary=Summaries.RECIPIENT_FILES_LIST)
async def list_recipient_files(id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    user = db.scalar(select(User).where(User.id == id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Errors.RECIPIENT_NOT_FOUND)
    _assert_can_access_recipient(db, id, current_user)
    items = docs.list_docs(corpus_uri=user.corpus_uri)
    return {Keys.RECIPIENT_ID: id, Keys.ITEMS: items}


@router.get(Routes.FILE_ID, summary=Summaries.FILE_DOWNLOAD)
async def get_recipient_file(id: str, fileId: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    user = db.scalar(select(User).where(User.id == id))
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=Errors.RECIPIENT_NOT_FOUND)
    _assert_can_access_recipient(db, id, current_user)
    doc = docs.get_doc(corpus_uri=user.corpus_uri, doc_id=fileId)
    return {Keys.RECIPIENT_ID: id, Keys.FILE_ID: fileId, Keys.DATA: doc}


@router.delete(Routes.FILE_ID, status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.FILE_DELETE)
async def delete_recipient_file(id: str, fileId: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> None:
    user = db.scalar(select(User).where(User.id == id))
    if user is None:
        raise HTTPException(status_code=404, detail=Errors.RECIPIENT_NOT_FOUND)
    _assert_can_access_recipient(db, id, current_user)
    docs.delete_doc(corpus_uri=user.corpus_uri, doc_id=fileId)
    return


