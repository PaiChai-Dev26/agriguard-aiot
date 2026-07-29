from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import StrEnum


class IncidentState(StrEnum):
    NORMAL = "normal"
    SUSPECTED = "suspected"
    PENDING_CONFIRMATION = "pending_confirmation"
    CANCELLED = "cancelled"
    DETECTED = "detected"
    ACKNOWLEDGED = "acknowledged"
    DISPATCHED = "dispatched"
    RESOLVED = "resolved"


@dataclass
class Incident:
    state: IncidentState = IncidentState.NORMAL
    confirmation_deadline: datetime | None = None

    def suspect(self, now: datetime | None = None) -> None:
        self._require(IncidentState.NORMAL)
        now = now or datetime.now(timezone.utc)
        self.state = IncidentState.SUSPECTED
        self.state = IncidentState.PENDING_CONFIRMATION
        self.confirmation_deadline = now + timedelta(seconds=10)

    def cancel(self) -> None:
        self._require(IncidentState.PENDING_CONFIRMATION)
        self.state = IncidentState.CANCELLED

    def confirm_if_due(self, now: datetime | None = None) -> bool:
        self._require(IncidentState.PENDING_CONFIRMATION)
        now = now or datetime.now(timezone.utc)
        if self.confirmation_deadline is None or now < self.confirmation_deadline:
            return False
        self.state = IncidentState.DETECTED
        return True

    def acknowledge(self) -> None:
        self._transition(IncidentState.DETECTED, IncidentState.ACKNOWLEDGED)

    def dispatch(self) -> None:
        self._transition(IncidentState.ACKNOWLEDGED, IncidentState.DISPATCHED)

    def resolve(self) -> None:
        if self.state not in {IncidentState.DETECTED, IncidentState.ACKNOWLEDGED, IncidentState.DISPATCHED}:
            raise ValueError(f"cannot resolve incident from {self.state}")
        self.state = IncidentState.RESOLVED

    def _transition(self, expected: IncidentState, target: IncidentState) -> None:
        self._require(expected)
        self.state = target

    def _require(self, expected: IncidentState) -> None:
        if self.state != expected:
            raise ValueError(f"expected {expected}, got {self.state}")

