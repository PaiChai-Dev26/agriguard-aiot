from datetime import datetime, timedelta, timezone

import pytest

from backend.app.services.incident import Incident, IncidentState


def test_suspected_incident_can_be_cancelled() -> None:
    incident = Incident()
    incident.suspect()
    incident.cancel()
    assert incident.state == IncidentState.CANCELLED


def test_incident_is_detected_only_after_confirmation_deadline() -> None:
    started = datetime(2026, 8, 1, tzinfo=timezone.utc)
    incident = Incident()
    incident.suspect(started)

    assert incident.confirm_if_due(started + timedelta(seconds=9)) is False
    assert incident.confirm_if_due(started + timedelta(seconds=10)) is True
    assert incident.state == IncidentState.DETECTED


def test_invalid_transition_is_rejected() -> None:
    with pytest.raises(ValueError):
        Incident().acknowledge()

