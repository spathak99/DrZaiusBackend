from typing import Any, Dict, List
from backend.core.constants import Messages, Keys, Fields


class FilesService:
    def upload(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return {Keys.MESSAGE: Messages.FILE_UPLOADED, Keys.DATA: data}

    def get(self, file_id: str) -> Dict[str, Any]:
        return {Fields.ID: file_id}

    def delete(self, file_id: str) -> None:
        return

    def list_access(self, file_id: str) -> List[Dict[str, Any]]:
        return []

    def grant_access(self, file_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return {Keys.MESSAGE: Messages.ACCESS_GRANTED, Keys.FILE_ID: file_id, Keys.DATA: data}

    def update_access(self, file_id: str, caregiver_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            Keys.MESSAGE: Messages.ACCESS_UPDATED,
            Keys.FILE_ID: file_id,
            Keys.CAREGIVER_ID: caregiver_id,
            Keys.DATA: data,
        }

    def revoke_access(self, file_id: str, caregiver_id: str) -> None:
        return


