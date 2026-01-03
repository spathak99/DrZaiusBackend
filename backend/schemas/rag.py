from __future__ import annotations

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class RagQueryRequest(BaseModel):
	query: str = Field(..., description="Free text query.")
	top_k: Optional[int] = Field(default=5, description="Max number of results to return.")


class RagQueryResponse(BaseModel):
	id: str = Field(..., description="Current user id.")
	results: List[Dict[str, Any]] = Field(default_factory=list, description="RAG search results.")


