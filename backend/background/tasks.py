import uuid
from typing import Dict, Any, Optional


def enqueue_embedding_job(resource_type: str, resource_id: str, payload: Optional[Dict[str, Any]] = None) -> str:
    return str(uuid.uuid4())


def enqueue_ingestion_job(source_id: str, payload: Optional[Dict[str, Any]] = None) -> str:
    return str(uuid.uuid4())


