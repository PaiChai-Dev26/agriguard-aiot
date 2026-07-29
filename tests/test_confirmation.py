import asyncio
from datetime import datetime, timedelta, timezone

from backend.app.repositories.incidents import InMemoryIncidentRepository
from backend.app.schemas import IncidentRead, RiskResult
from backend.app.services.confirmation import confirm_due_incidents


class Recorder:
    def __init__(self) -> None:
        self.events: list[dict] = []

    async def broadcast(self, event: dict) -> None:
        self.events.append(event)


def test_due_incident_is_confirmed_and_broadcast(incident_id) -> None:
    now = datetime.now(timezone.utc)
    repository = InMemoryIncidentRepository()
    repository.add(
        IncidentRead(
            id=incident_id,
            deviceId="tractor-001",
            occurredAt=now - timedelta(seconds=20),
            status="pending_confirmation",
            confirmationDeadline=now - timedelta(seconds=10),
            risk=RiskResult(
                classification="rollover",
                riskScore=1,
                evidence=["dangerous_tilt", "impact", "inactivity"],
                modelVersion="rules-v1",
            ),
        )
    )
    recorder = Recorder()
    count = asyncio.run(confirm_due_incidents(repository, recorder, now))
    assert count == 1
    assert repository.get(incident_id).status == "detected"
    assert recorder.events[0]["type"] == "incident.detected"

