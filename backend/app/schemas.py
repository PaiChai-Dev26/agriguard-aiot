from datetime import datetime, timezone
from enum import StrEnum

from pydantic import BaseModel, Field, model_validator


class IncidentState(StrEnum):
    NORMAL = "normal"
    SUSPECTED = "suspected"
    PENDING_CONFIRMATION = "pending_confirmation"
    DETECTED = "detected"
    CANCELLED = "cancelled"


class Location(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    accuracy_m: float | None = Field(default=None, ge=0)


class Telemetry(BaseModel):
    type: str = "device.telemetry"
    device_id: str = Field(min_length=1, max_length=64)
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    ax: float
    ay: float
    az: float
    gx: float
    gy: float
    gz: float
    roll: float
    pitch: float
    speed_kmh: float = Field(default=0, ge=0)
    motion_rms: float = Field(default=0, ge=0)
    location: Location | None = None
    battery_percent: int | None = Field(default=None, ge=0, le=100)

    @model_validator(mode="after")
    def ensure_timezone(self) -> "Telemetry":
        if self.occurred_at.tzinfo is None:
            raise ValueError("occurred_at must include a timezone")
        return self


class RiskAssessment(BaseModel):
    score: float = Field(ge=0, le=1)
    label: str
    reasons: list[str]
    model_version: str = "rules-v1"


class TelemetryResult(BaseModel):
    telemetry: Telemetry
    risk: RiskAssessment
    incident_state: IncidentState
    confirmation_remaining_seconds: float | None = None


class IncidentEvent(BaseModel):
    type: str
    event_id: str
    device_id: str
    occurred_at: datetime
    status: IncidentState
    risk_score: float
    reasons: list[str]
    location: Location | None = None

