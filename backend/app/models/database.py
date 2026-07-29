from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import JSON, Boolean, DateTime, Float, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class DeviceRow(Base):
    __tablename__ = "devices"

    device_id: Mapped[str] = mapped_column(String(80), primary_key=True)
    display_name: Mapped[str] = mapped_column(String(100))
    device_type: Mapped[str] = mapped_column(String(20))
    registered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_seen_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    online: Mapped[bool] = mapped_column(Boolean, default=False)
    battery_percent: Mapped[int | None] = mapped_column(Integer)
    solar_charging: Mapped[bool | None] = mapped_column(Boolean)


class TelemetryRow(Base):
    __tablename__ = "telemetry"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    device_id: Mapped[str] = mapped_column(ForeignKey("devices.device_id"))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    accel_x: Mapped[float] = mapped_column(Float)
    accel_y: Mapped[float] = mapped_column(Float)
    accel_z: Mapped[float] = mapped_column(Float)
    gyro_x: Mapped[float] = mapped_column(Float)
    gyro_y: Mapped[float] = mapped_column(Float)
    gyro_z: Mapped[float] = mapped_column(Float)
    roll: Mapped[float] = mapped_column(Float)
    pitch: Mapped[float] = mapped_column(Float)
    impact_g: Mapped[float] = mapped_column(Float)
    inactive_seconds: Mapped[float] = mapped_column(Float)
    speed_kph: Mapped[float | None] = mapped_column(Float)
    battery_percent: Mapped[int | None] = mapped_column(Integer)
    solar_charging: Mapped[bool] = mapped_column(Boolean, default=False)


class IncidentRow(Base):
    __tablename__ = "incidents"

    incident_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    device_id: Mapped[str] = mapped_column(ForeignKey("devices.device_id"))
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    status: Mapped[str] = mapped_column(String(30), index=True)
    confirmation_deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    classification: Mapped[str] = mapped_column(String(20))
    risk_score: Mapped[float] = mapped_column(Float)
    evidence: Mapped[list[str]] = mapped_column(JSON, default=list)
    model_version: Mapped[str] = mapped_column(String(50))


class SupportAlertRow(Base):
    __tablename__ = "support_alerts"

    alert_id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    incident_id: Mapped[UUID] = mapped_column(ForeignKey("incidents.incident_id"))
    target_device_id: Mapped[str] = mapped_column(ForeignKey("devices.device_id"))
    distance_meters: Mapped[float] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    status: Mapped[str] = mapped_column(String(20), default="pending")
    responded_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

