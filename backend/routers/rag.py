from typing import Any, Dict, Optional
from fastapi import APIRouter, Body, Depends, HTTPException, status
from backend.core.constants import Prefix, Tags, Summaries, Keys, Fields, Errors, Routes, RagKeys, DocKeys
from backend.core.exceptions import AppError, to_http, RagProviderError
from backend.routers.deps import get_current_user
from backend.db.models import User
from backend.schemas.rag import RagQueryRequest, RagQueryResponse
from backend.core.settings import get_settings
from backend.clients import VertexRagClient


router = APIRouter(prefix=Prefix.RAG, tags=[Tags.RAG], dependencies=[Depends(get_current_user)])
settings = get_settings()
client = VertexRagClient()


@router.post(Routes.QUERY, summary=Summaries.RAG_QUERY, response_model=RagQueryResponse)
async def rag_query(payload: RagQueryRequest = Body(default=None), current_user: User = Depends(get_current_user)) -> Dict[str, Any]:
    if not current_user.corpus_uri:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=Errors.CORPUS_URI_NOT_SET)
    if payload is None or not (payload.query or "").strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=Errors.INVALID_PAYLOAD)
    q = payload.query
    top_k = payload.top_k or 5
    if settings.enable_vertex:
        try:
            res = client.query(corpus_uri=current_user.corpus_uri, query_text=q, top_k=top_k)
            results = res.get(Keys.RESULTS, [])
        except AppError as e:
            raise to_http(e)
        except Exception:
            # Fallback to a mock result rather than failing
            results = [{RagKeys.SCORE: 0.0, RagKeys.SNIPPET: "RAG temporarily unavailable", DocKeys.DOC_ID: "fallback"}]
    else:
        results = [{RagKeys.SCORE: 0.9, RagKeys.SNIPPET: f"Mocked result for '{q}'", DocKeys.DOC_ID: "mock-1"}]
    return {Fields.ID: current_user.id, Keys.RESULTS: results}


