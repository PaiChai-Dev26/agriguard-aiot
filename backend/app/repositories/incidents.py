from threading import RLock
from uuid import UUID

from backend.app.schemas import IncidentRead


class IncidentNotFoundError(KeyError):
    pass


class InMemoryIncidentRepository:
    """Thread-safe development repository behind a replaceable interface."""

    def __init__(self) -> None:
        self._items: dict[UUID, IncidentRead] = {}
        self._lock = RLock()

    def add(self, incident: IncidentRead) -> IncidentRead:
        with self._lock:
            self._items[incident.id] = incident
        return incident

    def get(self, incident_id: UUID) -> IncidentRead:
        with self._lock:
            incident = self._items.get(incident_id)
        if incident is None:
            raise IncidentNotFoundError(str(incident_id))
        return incident

    def list(self) -> list[IncidentRead]:
        with self._lock:
            return sorted(self._items.values(), key=lambda item: item.occurred_at, reverse=True)

    def replace(self, incident: IncidentRead) -> IncidentRead:
        self.get(incident.id)
        with self._lock:
            self._items[incident.id] = incident
        return incident

    def clear(self) -> None:
        with self._lock:
            self._items.clear()

