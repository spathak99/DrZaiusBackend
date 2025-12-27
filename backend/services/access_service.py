from typing import Any, Dict, List
from backend.core.constants import Messages, Fields, Keys
from backend.schemas.common import AccessLevel


class AccessService:
    def list_recipient_caregivers(self, recipient_id: str) -> List[Dict[str, Any]]:
        return []

    def assign_caregiver(self, recipient_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            Keys.MESSAGE: Messages.CAREGIVER_ASSIGNED,
            Fields.ACCESS_LEVEL: data.get(Fields.ACCESS_LEVEL),
            Keys.RECIPIENT_ID: recipient_id,
            Keys.DATA: data,
        }

    def revoke_caregiver(self, recipient_id: str, caregiver_id: str) -> None:
        return

    def update_caregiver_access(self, recipient_id: str, caregiver_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return {
            Keys.MESSAGE: Messages.ACCESS_UPDATED,
            Keys.RECIPIENT_ID: recipient_id,
            Keys.CAREGIVER_ID: caregiver_id,
            Keys.DATA: data,
        }

    def list_caregiver_recipients(self, caregiver_id: str) -> List[Dict[str, Any]]:
        return []

    def get_caregiver_recipient(self, caregiver_id: str, recipient_id: str) -> Dict[str, Any]:
        return {Keys.CAREGIVER_ID: caregiver_id, Keys.RECIPIENT_ID: recipient_id, Fields.ACCESS_LEVEL: AccessLevel.read}

