from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from backend.app.repositories.replays import InMemoryReplayRepository, ReplayNotFoundError
from backend.app.schemas import ImuSample, Telemetry


def sample(occurred_at: datetime) -> Telemetry:
    return Telemetry(
        deviceId="tractor-001",
        occurredAt=occurred_at,
        imu=ImuSample(
            accelX=0, accelY=0, accelZ=1,
            gyroX=0, gyroY=0, gyroZ=0,
            roll=0, pitch=0,
        ),
    )


def test_buffer_keeps_only_last_thirty_seconds() -> None:
    repository = InMemoryReplayRepository()
    now = datetime.now(timezone.utc)
    for seconds_ago in (40, 30, 20, 0):
        repository.record(sample(now - timedelta(seconds=seconds_ago)))
    replay = repository.snapshot(uuid4(), "tractor-001")
    assert len(replay.samples) == 3
    assert replay.started_at == now - timedelta(seconds=30)


def test_snapshot_is_stable_after_new_telemetry() -> None:
    repository = InMemoryReplayRepository()
    now = datetime.now(timezone.utc)
    incident_id = uuid4()
    repository.record(sample(now))
    repository.snapshot(incident_id, "tractor-001")
    repository.record(sample(now + timedelta(seconds=1)))
    assert len(repository.get(incident_id).samples) == 1


def test_missing_replay_is_rejected() -> None:
    with pytest.raises(ReplayNotFoundError):
        InMemoryReplayRepository().get(uuid4())

