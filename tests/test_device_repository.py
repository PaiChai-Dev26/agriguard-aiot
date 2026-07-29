from datetime import datetime, timezone

import pytest

from backend.app.repositories.devices import (
    DeviceAlreadyExistsError,
    DeviceNotFoundError,
    InMemoryDeviceRepository,
)
from backend.app.schemas import DevicePosition, DeviceRead, ImuSample, Location, Telemetry


def device(device_id: str = "tractor-001") -> DeviceRead:
    return DeviceRead(
        deviceId=device_id,
        displayName="1번 트랙터",
        deviceType="tractor",
        registeredAt=datetime.now(timezone.utc),
    )


def test_device_repository_round_trip() -> None:
    repository = InMemoryDeviceRepository()
    expected = repository.add(device())
    assert repository.get(expected.device_id) == expected
    assert repository.list() == [expected]


def test_duplicate_device_is_rejected() -> None:
    repository = InMemoryDeviceRepository()
    repository.add(device())
    with pytest.raises(DeviceAlreadyExistsError):
        repository.add(device())


def test_unknown_device_is_rejected() -> None:
    with pytest.raises(DeviceNotFoundError):
        InMemoryDeviceRepository().get("missing")


def test_position_history_preserves_order_and_limit() -> None:
    repository = InMemoryDeviceRepository()
    repository.add(device())
    for index in range(3):
        repository.add_position(
            DevicePosition(
                deviceId="tractor-001",
                recordedAt=datetime.now(timezone.utc),
                location=Location(latitude=36.3 + index * 0.001, longitude=127.5),
            )
        )
    history = repository.position_history("tractor-001", limit=2)
    assert len(history) == 2
    assert history[0].location.latitude < history[1].location.latitude


def test_telemetry_updates_presence_power_and_position() -> None:
    repository = InMemoryDeviceRepository()
    sample = Telemetry(
        deviceId="sim-001",
        occurredAt=datetime.now(timezone.utc),
        imu=ImuSample(
            accelX=0, accelY=0, accelZ=1,
            gyroX=0, gyroY=0, gyroZ=0,
            roll=0, pitch=0,
        ),
        location=Location(latitude=36.3, longitude=127.5),
        batteryPercent=42,
        solarCharging=True,
    )
    updated = repository.record_telemetry(sample)
    assert updated.online is True
    assert updated.battery_percent == 42
    assert updated.solar_charging is True
    assert repository.position_history("sim-001")[0].location == sample.location
