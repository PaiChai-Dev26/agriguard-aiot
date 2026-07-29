from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class ImuSample(BaseModel):
    accel_x: float = Field(alias="accelX")
    accel_y: float = Field(alias="accelY")
    accel_z: float = Field(alias="accelZ")
    gyro_x: float = Field(alias="gyroX")
    gyro_y: float = Field(alias="gyroY")
    gyro_z: float = Field(alias="gyroZ")
    roll: float
    pitch: float


class Location(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    speed_kph: float = Field(default=0, ge=0, alias="speedKph")
    valid: bool = True


class Telemetry(BaseModel):
    type: Literal["device.telemetry"] = "device.telemetry"
    device_id: str = Field(min_length=1, alias="deviceId")
    occurred_at: datetime = Field(alias="occurredAt")
    imu: ImuSample
    location: Location | None = None
    impact_g: float = Field(default=0, ge=0, alias="impactG")
    inactive_seconds: float = Field(default=0, ge=0, alias="inactiveSeconds")
    battery_percent: int = Field(default=100, ge=0, le=100, alias="batteryPercent")
    solar_charging: bool = Field(default=False, alias="solarCharging")


class RiskResult(BaseModel):
    classification: Literal["normal", "slope", "vibration", "rollover"]
    risk_score: float = Field(ge=0, le=1, alias="riskScore")
    evidence: list[str]
    model_version: str = Field(alias="modelVersion")

    model_config = {"populate_by_name": True}


IncidentStatus = Literal[
    "suspected",
    "pending_confirmation",
    "cancelled",
    "detected",
    "acknowledged",
    "dispatched",
    "resolved",
]


class IncidentRead(BaseModel):
    id: UUID
    device_id: str = Field(alias="deviceId")
    occurred_at: datetime = Field(alias="occurredAt")
    status: IncidentStatus
    risk: RiskResult
    location: Location | None = None
    confirmation_deadline: datetime | None = Field(default=None, alias="confirmationDeadline")

    model_config = {"populate_by_name": True}


class IncidentStatusUpdate(BaseModel):
    status: Literal["acknowledged", "dispatched", "resolved"]


class CancelIncident(BaseModel):
    reason: str = Field(default="operator_cancelled", min_length=1, max_length=200)
