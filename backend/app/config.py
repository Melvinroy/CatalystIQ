from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "CatalystIQ API"
    api_prefix: str = "/api/v1"
    cors_origin: str = "http://localhost:5173"

    data_provider: str = Field(default="mock", description="mock or polygon")

    polygon_api_key: str | None = None
    polygon_base_url: str = "https://api.polygon.io"

    supabase_url: str | None = None
    supabase_key: str | None = None
    supabase_table: str = "scanner_snapshots"


@lru_cache
def get_settings() -> Settings:
    return Settings()
