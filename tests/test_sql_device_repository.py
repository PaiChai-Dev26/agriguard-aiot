from datetime import datetime, timezone

import pytest
from sqlalchemy.orm import Session

from backend.app.db import build_engine
from backend.app.models.database import Base
from backend.app.repositories.devices import DeviceAlreadyExistsError
from backend.app.repositories.sql_devices import SqlDeviceRepository
from backend.app.schemas import DeviceRead


def repository() -> SqlDeviceRepository:
    engine = build_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    return SqlDeviceRepository(Session(engine))


def device(device_id: str) -> DeviceRead:
    return DeviceRead(
        deviceId=device_id,
        displayName=device_id,
        deviceType="tractor",
        registeredAt=datetime.now(timezone.utc),
    )


def test_sql_device_repository_round_trip_and_order() -> None:
    devices = repository()
    devices.add(device("tractor-002"))
    devices.add(device("tractor-001"))
    assert [item.device_id for item in devices.list()] == ["tractor-001", "tractor-002"]
    assert devices.get("tractor-001").display_name == "tractor-001"


def test_sql_device_repository_rejects_duplicate() -> None:
    devices = repository()
    devices.add(device("tractor-001"))
    with pytest.raises(DeviceAlreadyExistsError):
        devices.add(device("tractor-001"))


def test_sql_device_repository_updates_presence() -> None:
    devices = repository()
    original = devices.add(device("tractor-001"))
    devices.replace(original.model_copy(update={"online": True, "battery_percent": 70}))
    assert devices.get("tractor-001").online is True
    assert devices.get("tractor-001").battery_percent == 70

