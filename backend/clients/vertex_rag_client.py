from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import uuid4

from backend.core.settings import get_settings
from backend.core.constants import DocKeys, MimeTypes


class VertexRagClient:
    """
    Thin client stub for Vertex AI RAG Corpus APIs.
    Replace stubbed bodies with real google-cloud-aiplatform calls.
    """

    def __init__(self) -> None:
        self.settings = get_settings()
        self.project_id = self.settings.gcp_project_id
        self.location = self.settings.gcp_location
        self.endpoint = self.settings.vertex_rag_api_endpoint.format(location=self.location)

    def add_document(
        self,
        *,
        corpus_uri: str,
        file_name: str,
        content: bytes,
        mime_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        # STUB: Return a mock doc id
        return {
            DocKeys.DOC_ID: str(uuid4()),
            DocKeys.NAME: file_name,
            DocKeys.MIME_TYPE: mime_type or MimeTypes.APPLICATION_OCTET_STREAM,
        }

    def delete_document(self, *, corpus_uri: str, doc_id: str) -> None:
        # STUB: No-op
        return

    def get_document(self, *, corpus_uri: str, doc_id: str) -> Dict[str, Any]:
        # STUB: Return placeholder metadata
        return {
            DocKeys.DOC_ID: doc_id,
            DocKeys.NAME: f"{doc_id}.pdf",
            DocKeys.MIME_TYPE: MimeTypes.APPLICATION_PDF,
        }

    def list_documents(self, *, corpus_uri: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        # STUB: Return empty list
        return []

    def query(self, *, corpus_uri: str, query_text: str, top_k: int = 5) -> Dict[str, Any]:
        # STUB: Return simple mock
        return {"results": [], "query": query_text, "topK": top_k}


