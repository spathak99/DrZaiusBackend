from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings
from backend.core.constants import Gcp, VertexEndpoints


class Settings(BaseSettings):
    database_url: str = Field(
        default="postgresql+psycopg2://postgres:postgres@localhost:5432/drzaius",
        description="SQLAlchemy database URL for Postgres",
    )
    auth_secret: str = Field(
        default="dev-insecure-secret-change-me",
        description="Secret used to sign auth tokens (HS256)",
    )
    auth_token_exp_minutes: int = Field(
        default=60,
        description="Access token expiry in minutes",
    )
    auto_create_db: bool = Field(
        default=False,
        description="If true, create tables automatically on startup (dev only)",
    )
    cors_origins: List[str] = Field(default_factory=list)
    # GCP / Vertex settings
    gcp_project_id: str = Field(default="", description="GCP project id")
    gcp_location: str = Field(default=Gcp.DEFAULT_LOCATION, description="GCP region/location for Vertex AI")
    gcp_credentials_file: str = Field(
        default="",
        description="Optional path to a service account JSON file; leave empty to use ADC",
    )
    vertex_rag_api_endpoint: str = Field(
        default=VertexEndpoints.AIPLATFORM_ENDPOINT_TEMPLATE,
        description="Vertex AI RAG API endpoint (format with {location})",
    )
    vertex_agent_api_endpoint: str = Field(
        default=VertexEndpoints.AIPLATFORM_ENDPOINT_TEMPLATE,
        description="Vertex AI Agent API endpoint (format with {location})",
    )
    vertex_default_agent_id: str = Field(
        default="",
        description="Optional default Agent resource id to use for chat",
    )
    enable_vertex: bool = Field(
        default=False,
        description="When true, call Vertex clients instead of stubs",
    )
    enable_pipeline: bool = Field(
        default=False,
        description="When true, route uploads to temp bucket + Pub/Sub + DLP pipeline",
    )
    # DLP
    enable_dlp: bool = Field(
        default=False,
        description="When true, use Google Cloud DLP for redaction where available",
    )
    dlp_location: str = Field(
        default=Gcp.DEFAULT_LOCATION,
        description="GCP region/location for DLP",
    )
    dlp_min_likelihood: str = Field(
        default="POSSIBLE",
        description="Minimum likelihood for DLP findings (e.g., VERY_UNLIKELY, UNLIKELY, POSSIBLE, LIKELY, VERY_LIKELY)",
    )
    dlp_info_types: List[str] = Field(
        default_factory=list,
        description="Optional explicit list of DLP info types to inspect; empty = provider defaults",
    )
    invite_signing_secret: str = Field(
        default="dev-invite-secret-change-me",
        description="Secret used to sign invite deep links (HMAC-SHA256)",
    )
    sendgrid_api_key: str = Field(default="", description="SendGrid API key; leave empty to disable email send")
    email_from: str = Field(default="no-reply@example.com", description="From address for transactional emails")
    # Encryption (envelope) settings
    enable_encryption: bool = Field(
        default=False,
        description="When true, encrypt sensitive fields at rest (envelope encryption)",
    )
    encryption_provider: str = Field(
        default="env",
        description="Key provider: env | secret_manager | kms",
    )
    encryption_key_id: str = Field(
        default="",
        description="Logical key identifier (e.g., dek_2025_12); used in envelopes",
    )
    encryption_env_key_b64: str = Field(
        default="",
        description="Base64-encoded DEK when encryption_provider=env",
    )
    encryption_secret_id: str = Field(
        default="",
        description="Secret Manager secret id for DEK when encryption_provider=secret_manager",
    )
    kms_key_name: str = Field(
        default="",
        description="KMS key resource name (projects/.../locations/.../keyRings/.../cryptoKeys/...) when provider=kms",
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


