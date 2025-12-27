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

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


