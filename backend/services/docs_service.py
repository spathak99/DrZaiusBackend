from __future__ import annotations

from typing import Any, Dict, List, Optional

from backend.core.constants import Keys, Messages, DocKeys
from backend.clients import VertexRagClient


class DocsService:
    """
    Stub service for interacting with a user's corpus in Vertex AI RAG (or similar).
    This implementation returns mocked results for development.
    """

    def __init__(self, client: Optional[VertexRagClient] = None) -> None:
        # Allow injection for testing; default to client stub
        self.client = client or VertexRagClient()

    def list_docs(self, *, corpus_uri: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        docs = self.client.list_documents(corpus_uri=corpus_uri, limit=limit, offset=offset)
        return docs

    def get_doc(self, *, corpus_uri: str, doc_id: str) -> Dict[str, Any]:
        return self.client.get_document(corpus_uri=corpus_uri, doc_id=doc_id)

    def upload_doc(
        self, *, corpus_uri: str, file_name: str, content_type: Optional[str] = None, content: bytes = b""
    ) -> Dict[str, Any]:
        created = self.client.add_document(
            corpus_uri=corpus_uri, file_name=file_name, content=content, mime_type=content_type
        )
        # normalize response
        created[DocKeys.CORPUS] = corpus_uri
        created[Keys.MESSAGE] = Messages.FILE_UPLOADED
        return created

    def delete_doc(self, *, corpus_uri: str, doc_id: str) -> None:
        self.client.delete_document(corpus_uri=corpus_uri, doc_id=doc_id)
        return


