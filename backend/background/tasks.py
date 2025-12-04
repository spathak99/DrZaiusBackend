import uuid
from typing import Dict, Any


def enqueue_embedding_job(resource_type: str, resource_id: str, payload: Dict[str, Any] | None = None) -> str:
    return str(uuid.uuid4())


def enqueue_ingestion_job(source_id: str, payload: Dict[str, Any] | None = None) -> str:
    return str(uuid.uuid4())


