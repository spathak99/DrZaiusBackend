# Centralized constants for API metadata, tags, and route prefixes.
#
from typing import Final


# API metadata
API_TITLE: Final[str] = "DrZaius API"


class Tags:
    CHATS: Final[str] = "Chats"
    USER_CHATS: Final[str] = "User Chats"
    AUTH: Final[str] = "Auth"
    USERS: Final[str] = "Users"
    RECIPIENTS: Final[str] = "Recipients"
    RELATIONS: Final[str] = "Relations"
    CAREGIVERS: Final[str] = "Caregivers"
    RECIPIENT_DATA: Final[str] = "Recipient Data"
    ACCESS: Final[str] = "Access"
    SECURITY: Final[str] = "Security"
    COMPLIANCE: Final[str] = "Compliance"
    FILES: Final[str] = "Files"


class Prefix:
    CHATS: Final[str] = "/chats"
    USER_CHATS: Final[str] = "/users/{userId}/chats"
    AUTH: Final[str] = "/auth"
    USERS: Final[str] = "/users"
    RECIPIENTS: Final[str] = "/recipients"
    CAREGIVERS: Final[str] = "/caregivers"
    RECIPIENT_FILES: Final[str] = "/recipients/{id}/files"
    CAREGIVER_INVITATIONS: Final[str] = "/caregivers/{caregiverId}/invitations"
    RECIPIENT_INVITATIONS: Final[str] = "/recipients/{recipientId}/invitations"
    RECIPIENT_ACCESS: Final[str] = "/recipients/{recipientId}/caregivers"
    SECURITY_KEYS: Final[str] = "/security/keys"
    SECURITY_POLICIES: Final[str] = "/security/policies"
    COMPLIANCE: Final[str] = "/compliance"
    RECIPIENT_CAREGIVERS: Final[str] = "/recipients/{recipientId}/caregivers"
    FILES: Final[str] = "/files"


