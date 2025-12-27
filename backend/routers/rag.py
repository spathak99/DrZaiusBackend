from typing import Any, Dict, Optional
from fastapi import APIRouter, Body, Depends, HTTPException
from backend.core.constants import Prefix, Tags, Summaries, Keys, Fields, Errors, Routes, RagKeys
from backend.routers.deps import get_current_user
from backend.db.models import User
from pydantic import BaseModel
from backend.core.settings import get_settings
from backend.clients import VertexRagClient


router = APIRouter(prefix=Prefix.RAG, tags=[Tags.RAG], dependencies=[Depends(get_current_user)])
settings = get_settings()
client = VertexRagClient()


class RagQueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 5


@router.post(Routes.QUERY, summary=Summaries.RAG_QUERY)
async def rag_query(payload: RagQueryRequest = Body(default=None), current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    if not current_user.corpus_uri:
        raise HTTPException(status_code=400, detail=Errors.CORPUS_URI_NOT_SET)
    q = payload.query
    top_k = payload.top_k or 5
    if settings.enable_vertex:
        res = client.query(corpus_uri=current_user.corpus_uri, query_text=q, top_k=top_k)
        results = res.get(Keys.RESULTS, [])
    else:
        results = [
            {RagKeys.SCORE: 0.9, RagKeys.SNIPPET: f"Mocked result for '{q}'", "docId": "mock-1"},
        ]
    return {Fields.ID: current_user.id, Keys.RESULTS: results}


