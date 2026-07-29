from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest

from backend.app.repositories.incidents import IncidentNotFoundError, InMemoryIncidentRepository
from backend.app.schemas import IncidentRead, RiskResult


def incident() -> IncidentRead:
    return IncidentRead(
        id=uuid4(),
        deviceId="tractor-001",
        occurredAt=datetime.now(timezone.utc),
        status="detected",
        risk=RiskResult(
            classification="rollover",
            riskScore=0.95,
            evidence=["dangerous_tilt", "impact", "inactivity"],
            modelVersion="rules-v1",
        ),
    )


def test_repository_round_trip() -> None:
    repository = InMemoryIncidentRepository()
    expected = incident()
    repository.add(expected)
    assert repository.get(expected.id) == expected
    assert repository.list() == [expected]


def test_repository_rejects_unknown_id() -> None:
    with pytest.raises(IncidentNotFoundError):
        InMemoryIncidentRepository().get(uuid4())


def test_repository_finds_only_expired_pending_incidents() -> None:
    repository = InMemoryIncidentRepository()
    now = datetime.now(timezone.utc)
    due = incident().model_copy(
        update={
            "status": "pending_confirmation",
            "confirmation_deadline": now - timedelta(seconds=1),
        }
    )
    future = incident().model_copy(
        update={
            "status": "pending_confirmation",
            "confirmation_deadline": now + timedelta(seconds=1),
        }
    )
    repository.add(due)
    repository.add(future)
    repository.add(incident())
    assert repository.pending_due(now) == [due]
