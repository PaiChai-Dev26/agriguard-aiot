import os
from functools import lru_cache

from pydantic import BaseModel, Field


class Settings(BaseModel):
    app_name: str = "AgriGuard API"
    environment: str = "development"
    confirmation_seconds: int = Field(default=10, ge=1, le=60)
    nearby_radius_meters: int = Field(default=1000, ge=100, le=5000)
    database_url: str = "sqlite:///./agriguard.db"

    @classmethod
    def from_environment(cls) -> "Settings":
        values = {
            "environment": os.getenv("AGRIGUARD_ENVIRONMENT", "development"),
            "confirmation_seconds": os.getenv("AGRIGUARD_CONFIRMATION_SECONDS", "10"),
            "nearby_radius_meters": os.getenv("AGRIGUARD_NEARBY_RADIUS_METERS", "1000"),
            "database_url": os.getenv("AGRIGUARD_DATABASE_URL", "sqlite:///./agriguard.db"),
        }
        return cls.model_validate(values)


@lru_cache
def get_settings() -> Settings:
    return Settings.from_environment()
