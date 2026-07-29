from __future__ import annotations

from collections import defaultdict, deque
from datetime import timedelta
from threading import RLock
from uuid import UUID

from backend.app.schemas import IncidentReplay, Telemetry


class ReplayNotFoundError(KeyError):
    pass


class InMemoryReplayRepository:
    def __init__(self, window: timedelta = timedelta(seconds=30)) -> None:
        self._window = window
        self._buffers: dict[str, deque[Telemetry]] = defaultdict(deque)
        self._replays: dict[UUID, IncidentReplay] = {}
        self._lock = RLock()

    def record(self, sample: Telemetry) -> None:
        with self._lock:
            buffer = self._buffers[sample.device_id]
            buffer.append(sample)
            cutoff = sample.occurred_at - self._window
            while buffer and buffer[0].occurred_at < cutoff:
                buffer.popleft()

    def snapshot(self, incident_id: UUID, device_id: str) -> IncidentReplay:
        with self._lock:
            samples = list(self._buffers[device_id])
            if not samples:
                raise ReplayNotFoundError(device_id)
            replay = IncidentReplay(
                incidentId=incident_id,
                deviceId=device_id,
                startedAt=samples[0].occurred_at,
                endedAt=samples[-1].occurred_at,
                samples=samples,
            )
            self._replays[incident_id] = replay
        return replay

    def get(self, incident_id: UUID) -> IncidentReplay:
        with self._lock:
            replay = self._replays.get(incident_id)
        if replay is None:
            raise ReplayNotFoundError(str(incident_id))
        return replay

    def clear(self) -> None:
        with self._lock:
            self._buffers.clear()
            self._replays.clear()

