from typing import Any, Dict, List


class AccessService:
    def list_recipient_caregivers(self, recipient_id: str) -> List[Dict[str, Any]]:
        return []

    def assign_caregiver(self, recipient_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": "caregiver assigned", "recipientId": recipient_id, "data": data}

    def revoke_caregiver(self, recipient_id: str, caregiver_id: str) -> None:
        return

    def update_caregiver_access(self, recipient_id: str, caregiver_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        return {"message": "access updated", "recipientId": recipient_id, "caregiverId": caregiver_id, "data": data}

    def list_caregiver_recipients(self, caregiver_id: str) -> List[Dict[str, Any]]:
        return []

    def get_caregiver_recipient(self, caregiver_id: str, recipient_id: str) -> Dict[str, Any]:
        return {"caregiverId": caregiver_id, "recipientId": recipient_id, "access_level": "read"}


