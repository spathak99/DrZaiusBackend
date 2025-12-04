from functools import lru_cache
from typing import List

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = Field(
        default="postgresql+psycopg2://postgres:postgres@localhost:5432/drzaius",
        description="SQLAlchemy database URL for Postgres",
    )
    auto_create_db: bool = Field(
        default=False,
        description="If true, create tables automatically on startup (dev only)",
    )
    cors_origins: List[str] = Field(default_factory=list)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


