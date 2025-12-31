# Centralized constants for API metadata, tags, and route prefixes.
#
from typing import Final


# API metadata
API_TITLE: Final[str] = "DrZaius API"


class Tags:
    CHATS: Final[str] = "Chats"
    USER_CHATS: Final[str] = "User Chats"
    MESSAGES: Final[str] = "Messages"
    PARTICIPANTS: Final[str] = "Participants"
    AUTH: Final[str] = "Auth"
    USERS: Final[str] = "Users"
    RECIPIENTS: Final[str] = "Recipients"
    RELATIONS: Final[str] = "Relations"
    CAREGIVERS: Final[str] = "Caregivers"
    RECIPIENT_DATA: Final[str] = "Recipient Data"
    ACCESS: Final[str] = "Access"
    SECURITY: Final[str] = "Security"
    COMPLIANCE: Final[str] = "Compliance"
    OPS: Final[str] = "Ops"
    FILES: Final[str] = "Files"
    GROUPS: Final[str] = "Groups"
    RAG: Final[str] = "RAG"


class Prefix:
    CHATS: Final[str] = "/chats"
    CHAT_MESSAGES: Final[str] = "/chats/{chatId}/messages"
    CHAT_PARTICIPANTS: Final[str] = "/chats/{chatId}/participants"
    USER_CHATS: Final[str] = "/users/{userId}/chats"
    AUTH: Final[str] = "/auth"
    USERS: Final[str] = "/users"
    RECIPIENTS: Final[str] = "/recipients"
    CAREGIVERS: Final[str] = "/caregivers"
    CAREGIVER_RECIPIENTS: Final[str] = "/caregivers/{caregiverId}/recipients"
    RECIPIENT_FILES: Final[str] = "/recipients/{id}/files"
    CAREGIVER_INVITATIONS: Final[str] = "/caregivers/{caregiverId}/invitations"
    RECIPIENT_INVITATIONS: Final[str] = "/recipients/{recipientId}/invitations"
    RECIPIENT_ACCESS: Final[str] = "/recipients/{recipientId}/caregivers"
    SECURITY_KEYS: Final[str] = "/security/keys"
    SECURITY_POLICIES: Final[str] = "/security/policies"
    COMPLIANCE: Final[str] = "/compliance"
    RECIPIENT_CAREGIVERS: Final[str] = "/recipients/{recipientId}/caregivers"
    FILES: Final[str] = "/files"
    GROUPS: Final[str] = "/groups"
    GROUP_MEMBERS: Final[str] = "/groups/{groupId}/members"
    RAG: Final[str] = "/rag"
    REDACTION: Final[str] = "/redaction"
    INVITES: Final[str] = "/invites"

class Routes:
    ROOT: Final[str] = ""
    ID: Final[str] = "/{id}"
    USER_ID: Final[str] = "/{userId}"
    RECIPIENT_ID: Final[str] = "/{recipientId}"
    CHAT_ID: Final[str] = "/{chatId}"
    MESSAGE_ID: Final[str] = "/{messageId}"
    FILE_ID: Final[str] = "/{fileId}"
    CAREGIVER_ID: Final[str] = "/{caregiverId}"
    INVITATION_ID: Final[str] = "/{invitationId}"
    SELF: Final[str] = "/self"
    QUERY: Final[str] = "/query"
    # Auth
    AUTH_SIGNUP: Final[str] = "/signup"
    AUTH_LOGIN: Final[str] = "/login"
    AUTH_ME: Final[str] = "/me"
    AUTH_LOGOUT: Final[str] = "/logout"
    AUTH_CHANGE_PASSWORD: Final[str] = "/change-password"
    AVATAR: Final[str] = "/avatar"
    # Health
    HEALTHZ: Final[str] = "/healthz"
    READYZ: Final[str] = "/readyz"
    # Common suffixes
    EMBEDDINGS: Final[str] = "/embeddings"
    DOWNLOAD: Final[str] = "/download"
    ACCESS: Final[str] = "/access"
    ROLE: Final[str] = "/role"
    CODE: Final[str] = "/{code}"
    PAYMENTS: Final[str] = "/payments"
    CODES: Final[str] = "/codes"
    VOID: Final[str] = "/void"
    REDEEM: Final[str] = "/redeem"
    SENT: Final[str] = "/sent"
    ACCEPT_BY_TOKEN: Final[str] = "/accept-by-token"
    # Invitations actions
    INVITATION_ACCEPT: Final[str] = "/{invitationId}/accept"
    INVITATION_DECLINE: Final[str] = "/{invitationId}/decline"


class Summaries:
    LIST_CHATS: Final[str] = "Get a list of all chats"
    GET_CHAT: Final[str] = "Get a specific chat by ID"
    CREATE_CHAT: Final[str] = "Create a new chat"
    UPDATE_CHAT: Final[str] = "Update a chat by ID"
    DELETE_CHAT: Final[str] = "Delete a chat by ID"
    CHAT_EMBEDDINGS_CREATE: Final[str] = "Generate embeddings for a chat"
    CHAT_EMBEDDINGS_GET: Final[str] = "Get embeddings for a chat"
    MESSAGE_CREATE: Final[str] = "Create message in chat"
    MESSAGE_LIST: Final[str] = "List messages in chat"
    MESSAGE_GET: Final[str] = "Get message by ID"
    MESSAGE_UPDATE: Final[str] = "Update message by ID"
    MESSAGE_DELETE: Final[str] = "Delete message by ID"
    PARTICIPANTS_LIST: Final[str] = "List participants in a chat"
    PARTICIPANTS_ADD: Final[str] = "Add participant to a chat"
    PARTICIPANTS_REMOVE: Final[str] = "Remove participant from a chat"
    SIGNUP: Final[str] = "Create a new user account"
    LOGIN: Final[str] = "Log in and receive authentication token"
    LOGOUT: Final[str] = "Log out and invalidate token"
    CHANGE_PASSWORD: Final[str] = "Change current user's password"
    AUTH_ME: Final[str] = "Get current user"
    USERS_LIST: Final[str] = "Get a list of users"
    USER_CREATE: Final[str] = "Create a user (admin)"
    USER_GET: Final[str] = "Get a specific user by ID"
    USER_UPDATE: Final[str] = "Update user details"
    USER_DELETE: Final[str] = "Delete user (admin)"
    RECIPIENTS_LIST: Final[str] = "Get a list of all recipients"
    RECIPIENT_CREATE: Final[str] = "Register a new recipient (admin only)"
    RECIPIENT_GET: Final[str] = "Get a specific recipient's details"
    RECIPIENT_UPDATE: Final[str] = "Update a recipient's details"
    RECIPIENT_DELETE: Final[str] = "Delete a recipient"
    CAREGIVERS_LIST: Final[str] = "Get a list of all caregivers"
    CAREGIVER_CREATE: Final[str] = "Register a new caregiver"
    CAREGIVER_GET: Final[str] = "Get a specific caregiver's details"
    CAREGIVER_UPDATE: Final[str] = "Update a caregiver's details"
    CAREGIVER_DELETE: Final[str] = "Delete a user as caregiver"
    FILE_UPLOAD: Final[str] = "Upload a file"
    FILE_GET: Final[str] = "Get a specific file by ID"
    FILE_DELETE: Final[str] = "Delete a file by ID"
    FILE_EMBEDDINGS_CREATE: Final[str] = "Generate embeddings for a file"
    FILE_EMBEDDINGS_GET: Final[str] = "Get embeddings for a file"
    FILE_DOWNLOAD: Final[str] = "Download file by ID"
    FILE_ACCESS_LIST: Final[str] = "List file access control entries"
    FILE_ACCESS_GRANT: Final[str] = "Grant access to caregiver"
    FILE_ACCESS_UPDATE: Final[str] = "Update caregiver access level for file"
    FILE_ACCESS_REVOKE: Final[str] = "Revoke caregiver access to file"
    RECIPIENT_FILES_LIST: Final[str] = "Get a list of a recipient's files"
    RECIPIENT_CAREGIVERS_LIST: Final[str] = "Get a recipient's assigned caregivers"
    RECIPIENT_CAREGIVER_ASSIGN: Final[str] = "Assign caregiver to a recipient"
    RECIPIENT_CAREGIVER_REVOKE: Final[str] = "Recipient revokes caregiver access"
    RECIPIENT_CAREGIVER_UPDATE: Final[str] = "Update caregiver access level for recipient"
    CAREGIVER_RECIPIENTS_LIST: Final[str] = "List recipients assigned to caregiver"
    CAREGIVER_RECIPIENT_GET: Final[str] = "Get caregiver-recipient relationship details"
    INVITATIONS_SENT_LIST: Final[str] = "List invitations sent by caregiver"
    INVITATION_SEND: Final[str] = "Caregiver sends an invitation to a recipient"
    INVITATION_CANCEL: Final[str] = "Cancel a pending invitation"
    INVITATIONS_RECEIVED_LIST: Final[str] = "Get a recipient's received invitations"
    INVITATION_ACCEPT: Final[str] = "Recipient accepts a caregiver invitation"
    INVITATION_DECLINE: Final[str] = "Recipient declines a caregiver invitation"
    INVITATION_GET: Final[str] = "Get recipient invitation details"
    KEY_GENERATE: Final[str] = "Generate a new encryption key pair (admin only)"
    KEY_GET: Final[str] = "Get a specific encryption key (admin only)"
    POLICY_CREATE: Final[str] = "Create a new security policy (admin only)"
    POLICY_GET: Final[str] = "Get a specific security policy (admin only)"
    POLICY_UPDATE: Final[str] = "Update a security policy (admin only)"
    POLICY_DELETE: Final[str] = "Delete a security policy (admin only)"
    HIPAA_REPORT: Final[str] = "Generate a HIPAA compliance report"
    RISK_CREATE: Final[str] = "Initiate a new risk assessment"
    RISK_GET: Final[str] = "Get a specific risk assessment (admin only)"
    INCIDENT_CREATE: Final[str] = "Report a compliance incident or data breach"
    INCIDENT_GET: Final[str] = "Get details of a reported incident"
    HEALTHZ: Final[str] = "Liveness probe"
    READYZ: Final[str] = "Readiness probe"
    GROUPS_LIST: Final[str] = "List groups for current user"
    GROUP_CREATE: Final[str] = "Create a new group"
    GROUP_GET: Final[str] = "Get a specific group"
    GROUP_MEMBERS_LIST: Final[str] = "List members of a group"
    GROUP_MEMBER_ADD: Final[str] = "Add user to group (admin only)"
    GROUP_MEMBER_REMOVE: Final[str] = "Remove user from group (admin only)"
    GROUP_UPDATE: Final[str] = "Update group details (admin only)"
    GROUP_LEAVE: Final[str] = "Leave group"
    RAG_QUERY: Final[str] = "Query the Vertex RAG corpus"
    AVATAR_UPLOAD: Final[str] = "Upload user avatar"
    GROUP_DELETE: Final[str] = "Delete a group"
    GROUP_MEMBER_UPDATE: Final[str] = "Update group member role"
    PAYMENT_CODE_CREATE: Final[str] = "Create payment code"
    PAYMENT_CODES_LIST: Final[str] = "List payment codes"
    PAYMENT_CODE_VOID: Final[str] = "Void payment code"
    PAYMENT_CODE_REDEEM: Final[str] = "Redeem payment code"
    REDACTION_TEST: Final[str] = "Test redaction service with small text"


class Messages:
    OK: Final[str] = "ok"
    READY: Final[str] = "ready"
    SIGNUP_SUCCESSFUL: Final[str] = "signup successful"
    ACCESS_TOKEN_FAKE: Final[str] = "fake-token"
    TOKEN_TYPE_BEARER: Final[str] = "bearer"
    CHAT_CREATED: Final[str] = "chat created"
    CHAT_UPDATED: Final[str] = "chat updated"
    MESSAGE_CREATED: Final[str] = "message created"
    MESSAGE_UPDATED: Final[str] = "message updated"
    PARTICIPANT_ADDED: Final[str] = "participant added"
    FILE_UPLOADED: Final[str] = "file uploaded"
    FILE_QUEUED: Final[str] = "file queued for ingestion"
    ACCESS_GRANTED: Final[str] = "access granted"
    ACCESS_UPDATED: Final[str] = "access updated"
    EMBEDDINGS_JOB_ENQUEUED: Final[str] = "embeddings job enqueued"
    INVITATION_SENT: Final[str] = "invitation sent"
    INVITATION_ACCEPTED: Final[str] = "invitation accepted"
    INVITATION_DECLINED: Final[str] = "invitation declined"
    USER_CREATED: Final[str] = "user created"
    USER_UPDATED: Final[str] = "user updated"
    CAREGIVER_CREATED: Final[str] = "caregiver created"
    CAREGIVER_UPDATED: Final[str] = "caregiver updated"
    RECIPIENT_CREATED: Final[str] = "recipient created"
    RECIPIENT_UPDATED: Final[str] = "recipient updated"
    POLICY_CREATED: Final[str] = "policy created"
    POLICY_UPDATED: Final[str] = "policy updated"
    KEY_PAIR_GENERATED: Final[str] = "key pair generated"
    RISK_ASSESSMENT_STARTED: Final[str] = "risk assessment started"
    INCIDENT_REPORTED: Final[str] = "incident reported"
    CAREGIVER_ASSIGNED: Final[str] = "caregiver assigned"
    DLP_REDACTION_SCHEDULED: Final[str] = "redaction_scheduled"
    GROUP_MEMBER_ADDED: Final[str] = "group member added"
    GROUP_MEMBER_ROLE_UPDATED: Final[str] = "group member role updated"
    PAYMENT_CODE_CREATED: Final[str] = "payment code created"
    PAYMENT_CODE_REDEEMED: Final[str] = "payment code redeemed"


class Roles:
    RECIPIENT: Final[str] = "recipient"
    CAREGIVER: Final[str] = "caregiver"


class InvitationStatus:
    PENDING: Final[str] = "pending"
    ACCEPTED: Final[str] = "accepted"
    DECLINED: Final[str] = "declined"


class AccessLevel:
    READ: Final[str] = "read"
    WRITE: Final[str] = "write"
    ADMIN: Final[str] = "admin"


class Auth:
    JWT_HEADER_ALG: Final[str] = "alg"
    JWT_HEADER_TYP: Final[str] = "typ"
    JWT_ALG_HS256: Final[str] = "HS256"
    JWT_TYP_JWT: Final[str] = "JWT"
    JWT_CLAIM_SUB: Final[str] = "sub"
    JWT_CLAIM_IAT: Final[str] = "iat"
    JWT_CLAIM_EXP: Final[str] = "exp"
    PASSWORD_SCHEME_PBKDF2_SHA256: Final[str] = "pbkdf2_sha256"
    PBKDF2_HASH_NAME: Final[str] = "sha256"


class Errors:
    USERNAME_TAKEN: Final[str] = "username_taken"
    EMAIL_TAKEN: Final[str] = "email_taken"
    INVALID_CREDENTIALS: Final[str] = "invalid_credentials"
    UNAUTHORIZED: Final[str] = "unauthorized"
    MALFORMED_TOKEN: Final[str] = "malformed_token"
    MISSING_TOKEN: Final[str] = "missing_token"
    INVALID_TOKEN: Final[str] = "invalid_token"
    INVALID_PAYLOAD: Final[str] = "invalid_payload"
    RECIPIENT_NOT_FOUND: Final[str] = "recipient_not_found"
    CHAT_HISTORY_URI_NOT_SET: Final[str] = "chat_history_uri_not_set"
    GROUP_NOT_FOUND: Final[str] = "group_not_found"
    FORBIDDEN: Final[str] = "forbidden"
    USER_NOT_FOUND: Final[str] = "user_not_found"
    CORPUS_URI_NOT_SET: Final[str] = "corpus_uri_not_set"
    DB_UNAVAILABLE: Final[str] = "db_unavailable"
    MISSING_INGESTION_CONFIG: Final[str] = "missing_ingestion_config"
    INCORRECT_PASSWORD: Final[str] = "incorrect_password"
    RECIPIENT_NOT_REGISTERED: Final[str] = "recipient_not_registered"
    CAREGIVER_NOT_REGISTERED: Final[str] = "caregiver_not_registered"
    INTERNAL_ERROR: Final[str] = "internal_error"
    PAYLOAD_TOO_LARGE: Final[str] = "payload_too_large"
    UNSUPPORTED_MEDIA_TYPE: Final[str] = "unsupported_media_type"
    PAYMENT_CODE_NOT_FOUND: Final[str] = "payment_code_not_found"
    PAYMENT_CODE_EXPIRED: Final[str] = "payment_code_expired"
    PAYMENT_CODE_REDEEMED_ALREADY: Final[str] = "payment_code_redeemed_already"


class Defaults:
    # Storage and path defaults
    UPLOADS_PREFIX: Final[str] = "uploads"

class Upload:
    # Max file size for uploads (in MB)
    MAX_UPLOAD_MB: Final[int] = 15

class Fields:
    ID: Final[str] = "id"
    USERNAME: Final[str] = "username"
    EMAIL: Final[str] = "email"
    ROLE: Final[str] = "role"
    FULL_NAME: Final[str] = "full_name"
    PHONE_NUMBER: Final[str] = "phone_number"
    AGE: Final[str] = "age"
    COUNTRY: Final[str] = "country"
    AVATAR_URI: Final[str] = "avatar_uri"
    CREATED_AT: Final[str] = "created_at"
    UPDATED_AT: Final[str] = "updated_at"
    CORPUS_URI: Final[str] = "corpus_uri"
    CHAT_HISTORY_URI: Final[str] = "chat_history_uri"
    ACCESS_LEVEL: Final[str] = "access_level"
    NAME: Final[str] = "name"
    DESCRIPTION: Final[str] = "description"
    CREATED_BY: Final[str] = "created_by"
    GROUP_IDS: Final[str] = "group_ids"
    ACCOUNT_TYPE: Final[str] = "account_type"
    GROUP_ID: Final[str] = "group_id"
    GCP_PROJECT_ID: Final[str] = "gcp_project_id"
    TEMP_BUCKET: Final[str] = "temp_bucket"
    PAYMENT_INFO: Final[str] = "payment_info"

class Keys:
    MESSAGE: Final[str] = "message"
    ITEMS: Final[str] = "items"
    TOTAL: Final[str] = "total"
    DATA: Final[str] = "data"
    STATUS: Final[str] = "status"
    ACCEPT_URL: Final[str] = "acceptUrl"
    SENT_BY: Final[str] = "sent_by"
    JOB_ID: Final[str] = "jobId"
    PROJECT_ID: Final[str] = "projectId"
    BUCKET: Final[str] = "bucket"
    OBJECT: Final[str] = "object"
    VERTEX_ENABLED: Final[str] = "vertexEnabled"
    DOWNLOAD: Final[str] = "download"
    EMBEDDINGS: Final[str] = "embeddings"
    REQUEST_ID: Final[str] = "requestId"
    DB: Final[str] = "db"
    ENABLE_PIPELINE: Final[str] = "enablePipeline"
    ENABLE_DLP: Final[str] = "enableDlp"
    TYPE: Final[str] = "type"
    # Entity Id keys
    CHAT_ID: Final[str] = "chatId"
    FILE_ID: Final[str] = "fileId"
    RECIPIENT_ID: Final[str] = "recipientId"
    CAREGIVER_ID: Final[str] = "caregiverId"
    INVITATION_ID: Final[str] = "invitationId"
    USER_ID: Final[str] = "userId"
    GROUP_ID: Final[str] = "groupId"
    RESULTS: Final[str] = "results"
    SENDER_ID: Final[str] = "sender_id"
    SENDER_EMAIL: Final[str] = "sender_email"
    SENDER_FULL_NAME: Final[str] = "sender_full_name"
    TOKEN: Final[str] = "token"
    CODE: Final[str] = "code"
    EXPIRES_AT: Final[str] = "expires_at"
    REDEEMED_BY: Final[str] = "redeemed_by"
    INVITED_EMAIL: Final[str] = "invited_email"
    INVITED_FULL_NAME: Final[str] = "invited_full_name"

class Headers:
    TOTAL_COUNT: Final[str] = "X-Total-Count"
    REQUEST_ID: Final[str] = "X-Request-Id"


class RagKeys:
    SCORE: Final[str] = "score"
    SNIPPET: Final[str] = "snippet"


class Cors:
    DEFAULT_ORIGINS: Final[list[str]] = ["http://127.0.0.1:3000", "http://localhost:3000"]
    ALLOW_METHODS_ALL: Final[list[str]] = ["*"]
    ALLOW_HEADERS_ALL: Final[list[str]] = ["*"]

class Gcp:
    DEFAULT_LOCATION: Final[str] = "us-central1"

class VertexEndpoints:
    AIPLATFORM_ENDPOINT_TEMPLATE: Final[str] = "https://{location}-aiplatform.googleapis.com"

class Dlp:
    DEFAULT_MIN_LIKELIHOOD: Final[str] = "POSSIBLE"


class DocKeys:
    DOC_ID: Final[str] = "docId"
    NAME: Final[str] = "name"
    MIME_TYPE: Final[str] = "mimeType"
    SIZE_BYTES: Final[str] = "sizeBytes"
    CORPUS: Final[str] = "corpus"


class MimeTypes:
    APPLICATION_PDF: Final[str] = "application/pdf"
    APPLICATION_OCTET_STREAM: Final[str] = "application/octet-stream"
    APPLICATION_JSON: Final[str] = "application/json"
    TEXT_PLAIN: Final[str] = "text/plain"
    TEXT_HTML: Final[str] = "text/html"
    IMAGE_PNG: Final[str] = "image/png"
    IMAGE_JPEG: Final[str] = "image/jpeg"


class ChatKeys:
    MESSAGE_ID: Final[str] = "messageId"
    CHAT_ID: Final[str] = "chatId"
    ROLE: Final[str] = "role"
    CONTENT: Final[str] = "content"
    TIMESTAMP: Final[str] = "timestamp"
    PROVIDER: Final[str] = "provider"
    EXTERNAL_THREAD_ID: Final[str] = "externalThreadId"
    EXTERNAL_MESSAGE_ID: Final[str] = "externalMessageId"


class ChatRoles:
    USER: Final[str] = "user"
    ASSISTANT: Final[str] = "assistant"
    SYSTEM: Final[str] = "system"


class GroupRoles:
    ADMIN: Final[str] = "admin"
    MEMBER: Final[str] = "member"


class Tables:
    USERS: Final[str] = "users"
    GROUPS: Final[str] = "groups"
    GROUP_MEMBERSHIPS: Final[str] = "group_memberships"
    GROUP_MEMBER_INVITES: Final[str] = "group_member_invites"
    RECIPIENT_CAREGIVER_ACCESS: Final[str] = "recipient_caregiver_access"
    CHATS: Final[str] = "chats"
    CHAT_PARTICIPANTS: Final[str] = "chat_participants"
    MESSAGES: Final[str] = "messages"
    FILES: Final[str] = "files"
    FILE_ACCESS: Final[str] = "file_access"
    INVITATIONS: Final[str] = "invitations"
    GROUP_PAYMENT_CODES: Final[str] = "group_payment_codes"

class PaymentCodeStatus:
    ACTIVE: Final[str] = "active"
    EXPIRED: Final[str] = "expired"
    REDEEMED: Final[str] = "redeemed"

class Pagination:
    DEFAULT_LIMIT: Final[int] = 50
    MAX_LIMIT: Final[int] = 100
    DEFAULT_OFFSET: Final[int] = 0

class PaymentCodes:
    CODE_BYTES: Final[int] = 12


class LogEvents:
    GROUP_CREATED: Final[str] = "group_created"
    GROUP_UPDATED: Final[str] = "group_updated"
    GROUP_DELETED: Final[str] = "group_deleted"
    GROUP_MEMBER_ADDED: Final[str] = "group_member_added"
    GROUP_MEMBER_ROLE_CHANGED: Final[str] = "group_member_role_changed"
    GROUP_MEMBER_REMOVED: Final[str] = "group_member_removed"
    GROUP_MEMBER_LEFT: Final[str] = "group_member_left"
    PAYMENT_CODE_CREATED: Final[str] = "payment_code_created"
    PAYMENT_CODE_VOIDED: Final[str] = "payment_code_voided"
    PAYMENT_CODE_REDEEMED: Final[str] = "payment_code_redeemed"
    INVITATION_SENT: Final[str] = "invitation_sent"
    INVITATION_ACCEPTED: Final[str] = "invitation_accepted"
    INVITATION_DECLINED: Final[str] = "invitation_declined"
    FILE_QUEUED: Final[str] = "file_queued"
    FILE_UPLOADED: Final[str] = "file_uploaded"
    FILE_REDACT_QUEUED: Final[str] = "file_redact_queued"
    FILE_REDACT_UPLOADED: Final[str] = "file_redact_uploaded"

class TokenTypes:
    GROUP_MEMBER: Final[str] = "group_member"


class DeepLink:
    SCHEME: Final[str] = "drzaius"
    INVITE_ACCEPT_PATH: Final[str] = "invite/accept"


class Email:
    SUBJECT_INVITE: Final[str] = "You have a caregiver invitation"
    BODY_INVITED_PLAIN_PREFIX: Final[str] = "You've been invited. Accept here:"
    BODY_INVITED_HTML_PREFIX: Final[str] = "<p>You've been invited.</p>"
    HTML_LINK_LABEL: Final[str] = "Tap to accept"
    LINK_UNAVAILABLE: Final[str] = "(link unavailable)"
    HREF_FALLBACK: Final[str] = "#"


class Urls:
    SENDGRID_API_SEND: Final[str] = "https://api.sendgrid.com/v3/mail/send"
