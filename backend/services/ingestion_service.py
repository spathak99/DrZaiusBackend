import uuid
from typing import Dict, Any

from backend.core.settings import get_settings
from backend.core.constants import Keys


class IngestionService:
    def enqueue_ingestion(
        self,
        *,
        user_id: str,
        gcp_project_id: str,
        temp_bucket: str,
        file_name: str,
        content_type: str,
        content: bytes,
    ) -> Dict[str, Any]:
        """
        Stub: In a real implementation, this would:
        - Upload 'content' to the temp GCS bucket under a generated object name
        - Publish a Pub/Sub message with project/bucket/object and metadata
        For now, we return a mock jobId and the intended target locations.
        """
        settings = get_settings()
        object_name = f"uploads/{user_id}/{uuid.uuid4()}-{file_name}"
        job_id = str(uuid.uuid4())
        return {
            Keys.JOB_ID: job_id,
            Keys.PROJECT_ID: gcp_project_id,
            Keys.BUCKET: temp_bucket,
            Keys.OBJECT: object_name,
            Keys.VERTEX_ENABLED: settings.enable_vertex,
        }


