from datetime import datetime, timezone
from typing import Protocol

from backend.app.repositories.incidents import InMemoryIncidentRepository


class Broadcaster(Protocol):
    async def broadcast(self, event: dict) -> None: ...


async def confirm_due_incidents(
    repository: InMemoryIncidentRepository,
    broadcaster: Broadcaster,
    now: datetime | None = None,
) -> int:
    now = now or datetime.now(timezone.utc)
    confirmed = 0
    for incident in repository.pending_due(now):
        detected = incident.model_copy(update={"status": "detected"})
        repository.replace(detected)
        await broadcaster.broadcast(
            {
                "type": "incident.detected",
                "incident": detected.model_dump(mode="json", by_alias=True),
            }
        )
        confirmed += 1
    return confirmed

