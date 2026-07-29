"""Application-scoped repository instances.

Keeping construction here prevents API modules from importing one another and
provides a single replacement point for PostgreSQL-backed repositories.
"""

from backend.app.repositories.devices import InMemoryDeviceRepository
from backend.app.repositories.incidents import InMemoryIncidentRepository
from backend.app.repositories.replays import InMemoryReplayRepository
from backend.app.repositories.support_alerts import InMemorySupportAlertRepository

device_repository = InMemoryDeviceRepository()
incident_repository = InMemoryIncidentRepository()
replay_repository = InMemoryReplayRepository()
support_alert_repository = InMemorySupportAlertRepository()
