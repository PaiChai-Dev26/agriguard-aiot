from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.app.models.database import DeviceRow
from backend.app.repositories.devices import DeviceAlreadyExistsError, DeviceNotFoundError
from backend.app.schemas import DeviceRead


class SqlDeviceRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, device: DeviceRead) -> DeviceRead:
        self._session.add(self._to_row(device))
        try:
            self._session.commit()
        except IntegrityError as error:
            self._session.rollback()
            raise DeviceAlreadyExistsError(device.device_id) from error
        return device

    def get(self, device_id: str) -> DeviceRead:
        row = self._session.get(DeviceRow, device_id)
        if row is None:
            raise DeviceNotFoundError(device_id)
        return self._to_schema(row)

    def list(self) -> list[DeviceRead]:
        rows = self._session.scalars(select(DeviceRow).order_by(DeviceRow.device_id)).all()
        return [self._to_schema(row) for row in rows]

    def replace(self, device: DeviceRead) -> DeviceRead:
        row = self._session.get(DeviceRow, device.device_id)
        if row is None:
            raise DeviceNotFoundError(device.device_id)
        replacement = self._to_row(device)
        for column in (
            "display_name",
            "device_type",
            "registered_at",
            "last_seen_at",
            "online",
            "battery_percent",
            "solar_charging",
        ):
            setattr(row, column, getattr(replacement, column))
        self._session.commit()
        return device

    @staticmethod
    def _to_row(device: DeviceRead) -> DeviceRow:
        return DeviceRow(
            device_id=device.device_id,
            display_name=device.display_name,
            device_type=device.device_type,
            registered_at=device.registered_at,
            last_seen_at=device.last_seen_at,
            online=device.online,
            battery_percent=device.battery_percent,
            solar_charging=device.solar_charging,
        )

    @staticmethod
    def _to_schema(row: DeviceRow) -> DeviceRead:
        return DeviceRead(
            deviceId=row.device_id,
            displayName=row.display_name,
            deviceType=row.device_type,
            registeredAt=row.registered_at,
            lastSeenAt=row.last_seen_at,
            online=row.online,
            batteryPercent=row.battery_percent,
            solarCharging=row.solar_charging,
        )

