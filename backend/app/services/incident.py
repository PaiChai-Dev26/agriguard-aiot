from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import uuid4

from backend.app.schemas import (
    IncidentEvent,
    IncidentState,
    RiskAssessment,
    Telemetry,
)


@dataclass
class DeviceIncident:
    state: IncidentState = IncidentState.NORMAL
    suspected_at: datetime | None = None
    event_id: str | None = None


class IncidentStateMachine:
    def __init__(self, confirmation_seconds: float = 10.0) -> None:
        self.confirmation_seconds = confirmation_seconds
        self._devices: dict[str, DeviceIncident] = {}

    def state_for(self, device_id: str) -> DeviceIncident:
        return self._devices.setdefault(device_id, DeviceIncident())

    def process(
        self, sample: Telemetry, risk: RiskAssessment
    ) -> tuple[IncidentState, float | None, IncidentEvent | None]:
        incident = self.state_for(sample.device_id)
        event = None

        if incident.state in {IncidentState.CANCELLED, IncidentState.DETECTED}:
            return incident.state, None, None

        if risk.score >= 0.7 and incident.state == IncidentState.NORMAL:
            incident.state = IncidentState.SUSPECTED
            incident.suspected_at = sample.occurred_at
            incident.event_id = f"evt-{uuid4().hex[:12]}"
            event = self._event("incident.suspected", sample, risk, incident)

        if incident.state == IncidentState.SUSPECTED:
            incident.state = IncidentState.PENDING_CONFIRMATION

        remaining = None
        if incident.state == IncidentState.PENDING_CONFIRMATION:
            assert incident.suspected_at is not None
            deadline = incident.suspected_at + timedelta(seconds=self.confirmation_seconds)
            remaining = max((deadline - sample.occurred_at).total_seconds(), 0)
            if remaining == 0 and risk.score >= 0.7:
                incident.state = IncidentState.DETECTED
                remaining = None
                event = self._event("incident.detected", sample, risk, incident)
            elif risk.score < 0.3:
                self._devices[sample.device_id] = DeviceIncident()
                return IncidentState.NORMAL, None, None

        return incident.state, remaining, event

    def cancel(self, device_id: str, occurred_at: datetime) -> IncidentEvent | None:
        incident = self.state_for(device_id)
        if incident.state not in {
            IncidentState.SUSPECTED,
            IncidentState.PENDING_CONFIRMATION,
        }:
            return None
        incident.state = IncidentState.CANCELLED
        return IncidentEvent(
            type="incident.cancelled",
            event_id=incident.event_id or f"evt-{uuid4().hex[:12]}",
            device_id=device_id,
            occurred_at=occurred_at,
            status=IncidentState.CANCELLED,
            risk_score=0,
            reasons=["operator_cancelled"],
        )

    def reset(self, device_id: str) -> None:
        self._devices[device_id] = DeviceIncident()

    @staticmethod
    def _event(
        event_type: str,
        sample: Telemetry,
        risk: RiskAssessment,
        incident: DeviceIncident,
    ) -> IncidentEvent:
        return IncidentEvent(
            type=event_type,
            event_id=incident.event_id or f"evt-{uuid4().hex[:12]}",
            device_id=sample.device_id,
            occurred_at=sample.occurred_at,
            status=incident.state,
            risk_score=risk.score,
            reasons=risk.reasons,
            location=sample.location,
        )

