from typing import Any, Dict, List
from backend.core.constants import Messages


class FilesService:
    def upload(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": Messages.FILE_UPLOADED, "data": data}

    def get(self, file_id: str) -> Dict[str, Any]:
        return {"id": file_id}

    def delete(self, file_id: str) -> None:
        return

    def list_access(self, file_id: str) -> List[Dict[str, Any]]:
        return []

    def grant_access(self, file_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": Messages.ACCESS_GRANTED, "fileId": file_id, "data": data}

    def update_access(self, file_id: str, caregiver_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": Messages.ACCESS_UPDATED, "fileId": file_id, "caregiverId": caregiver_id, "data": data}

    def revoke_access(self, file_id: str, caregiver_id: str) -> None:
        return


