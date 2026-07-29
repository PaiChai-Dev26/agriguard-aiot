from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AgriGuard API"
    environment: str = "development"
    confirmation_seconds: int = Field(default=10, ge=1, le=60)
    nearby_radius_meters: int = Field(default=1000, ge=100, le=5000)
    database_url: str = "sqlite:///./agriguard.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="AGRIGUARD_",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

