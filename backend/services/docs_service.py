from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import uuid4

from backend.core.constants import Keys, Messages, DocKeys, MimeTypes


class DocsService:
    """
    Stub service for interacting with a user's corpus in Vertex AI RAG (or similar).
    This implementation returns mocked results for development.
    """

    def list_docs(self, *, corpus_uri: str, limit: int = 50, offset: int = 0) -> List[Dict[str, Any]]:
        # Return a stable mock list for given corpus_uri
        base = str(uuid4())[:8]
        docs = [
            {
                DocKeys.DOC_ID: f"{base}-000{i}",
                DocKeys.NAME: f"sample-{i}.pdf",
                DocKeys.MIME_TYPE: MimeTypes.APPLICATION_PDF,
                DocKeys.SIZE_BYTES: 10_000 + i,
                DocKeys.CORPUS: corpus_uri,
            }
            for i in range(3)
        ]
        return docs[offset : offset + limit]

    def get_doc(self, *, corpus_uri: str, doc_id: str) -> Dict[str, Any]:
        return {
            DocKeys.DOC_ID: doc_id,
            DocKeys.NAME: f"{doc_id}.pdf",
            DocKeys.MIME_TYPE: MimeTypes.APPLICATION_PDF,
            DocKeys.SIZE_BYTES: 12_345,
            DocKeys.CORPUS: corpus_uri,
        }

    def upload_doc(self, *, corpus_uri: str, file_name: str, content_type: Optional[str] = None) -> Dict[str, Any]:
        # In a real implementation, stream to corpus storage and return created metadata
        created_id = str(uuid4())
        return {
            Keys.MESSAGE: Messages.FILE_UPLOADED,
            DocKeys.DOC_ID: created_id,
            DocKeys.NAME: file_name,
            DocKeys.MIME_TYPE: content_type or MimeTypes.APPLICATION_OCTET_STREAM,
            DocKeys.CORPUS: corpus_uri,
        }

    def delete_doc(self, *, corpus_uri: str, doc_id: str) -> None:
        # No-op stub
        return


