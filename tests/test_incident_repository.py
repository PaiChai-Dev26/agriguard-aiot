from datetime import datetime, timezone
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

