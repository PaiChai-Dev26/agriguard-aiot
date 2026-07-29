from datetime import datetime, timezone
from uuid import uuid4

import pytest

from backend.app.schemas import IncidentRead, Location, RiskResult
from backend.app.services.sos import SosUnavailableError, create_sos_payload


def detected_incident(status: str = "detected", with_location: bool = True) -> IncidentRead:
    return IncidentRead(
        id=uuid4(),
        deviceId="tractor-001",
        occurredAt=datetime.now(timezone.utc),
        status=status,
        location=Location(latitude=36.3012, longitude=127.5874) if with_location else None,
        risk=RiskResult(
            classification="rollover",
            riskScore=0.94,
            evidence=["dangerous_tilt", "impact", "inactivity"],
            modelVersion="rules-v1",
        ),
    )


def test_create_sos_payload_for_detected_incident() -> None:
    sos = create_sos_payload(detected_incident())
    assert sos.type == "sos.created"
    assert sos.emergency_call_uri == "tel:119"
    assert "94%" in sos.summary


@pytest.mark.parametrize("status", ["suspected", "pending_confirmation", "cancelled", "resolved"])
def test_reject_unconfirmed_incident(status: str) -> None:
    with pytest.raises(SosUnavailableError):
        create_sos_payload(detected_incident(status))


def test_reject_incident_without_location() -> None:
    with pytest.raises(SosUnavailableError):
        create_sos_payload(detected_incident(with_location=False))

