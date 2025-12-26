from typing import Any, Dict
from fastapi import APIRouter, status, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.core.constants import Prefix, Tags, Summaries, Messages, Routes, Keys, Errors
from backend.db.database import get_db
from backend.db.models import User
from backend.services import DocsService
from backend.routers.deps import get_current_user


router = APIRouter(prefix=Prefix.RECIPIENT_FILES, tags=[Tags.RECIPIENT_DATA], dependencies=[Depends(get_current_user)])
docs = DocsService()


@router.post(Routes.ROOT, status_code=status.HTTP_201_CREATED, summary=Summaries.FILE_UPLOAD)
async def upload_recipient_file(id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    user = db.scalar(select(User).where(User.id == id))
    if user is None:
        raise HTTPException(status_code=404, detail=Errors.RECIPIENT_NOT_FOUND)
    # Mocked upload; in reality accept file upload. Here we fake a document name.
    created = docs.upload_doc(corpus_uri=user.corpus_uri, file_name=f"recipient-{id}-doc.pdf", content_type="application/pdf")
    return {Keys.MESSAGE: Messages.FILE_UPLOADED, Keys.RECIPIENT_ID: id, Keys.DATA: created}


@router.get(Routes.ROOT, summary=Summaries.RECIPIENT_FILES_LIST)
async def list_recipient_files(id: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    user = db.scalar(select(User).where(User.id == id))
    if user is None:
        raise HTTPException(status_code=404, detail=Errors.RECIPIENT_NOT_FOUND)
    items = docs.list_docs(corpus_uri=user.corpus_uri)
    return {Keys.RECIPIENT_ID: id, Keys.ITEMS: items}


@router.get(Routes.FILE_ID, summary=Summaries.FILE_DOWNLOAD)
async def get_recipient_file(id: str, fileId: str, db: Session = Depends(get_db)) -> Dict[str, Any]:
    user = db.scalar(select(User).where(User.id == id))
    if user is None:
        raise HTTPException(status_code=404, detail=Errors.RECIPIENT_NOT_FOUND)
    doc = docs.get_doc(corpus_uri=user.corpus_uri, doc_id=fileId)
    return {Keys.RECIPIENT_ID: id, Keys.FILE_ID: fileId, Keys.DATA: doc}


@router.delete(Routes.FILE_ID, status_code=status.HTTP_204_NO_CONTENT, summary=Summaries.FILE_DELETE)
async def delete_recipient_file(id: str, fileId: str, db: Session = Depends(get_db)) -> None:
    user = db.scalar(select(User).where(User.id == id))
    if user is None:
        raise HTTPException(status_code=404, detail="recipient_not_found")
    docs.delete_doc(corpus_uri=user.corpus_uri, doc_id=fileId)
    return


