from __future__ import annotations

from threading import RLock
from uuid import UUID

from backend.app.schemas import SupportAlert


class SupportAlertNotFoundError(KeyError):
    pass


class InMemorySupportAlertRepository:
    def __init__(self) -> None:
        self._alerts: dict[UUID, SupportAlert] = {}
        self._lock = RLock()

    def add(self, alert: SupportAlert) -> SupportAlert:
        with self._lock:
            duplicate = any(
                existing.incident_id == alert.incident_id
                and existing.target_device_id == alert.target_device_id
                for existing in self._alerts.values()
            )
            if duplicate:
                raise ValueError("support alert already exists")
            self._alerts[alert.id] = alert
        return alert

    def get(self, alert_id: UUID) -> SupportAlert:
        with self._lock:
            alert = self._alerts.get(alert_id)
        if alert is None:
            raise SupportAlertNotFoundError(str(alert_id))
        return alert

    def for_incident(self, incident_id: UUID) -> list[SupportAlert]:
        with self._lock:
            return sorted(
                (alert for alert in self._alerts.values() if alert.incident_id == incident_id),
                key=lambda alert: alert.distance_meters,
            )

    def for_device(self, device_id: str) -> list[SupportAlert]:
        with self._lock:
            return sorted(
                (alert for alert in self._alerts.values() if alert.target_device_id == device_id),
                key=lambda alert: alert.created_at,
                reverse=True,
            )

    def replace(self, alert: SupportAlert) -> SupportAlert:
        self.get(alert.id)
        with self._lock:
            self._alerts[alert.id] = alert
        return alert

    def clear(self) -> None:
        with self._lock:
            self._alerts.clear()

