from __future__ import annotations

from threading import RLock

from backend.app.schemas import DevicePosition, DeviceRead, Telemetry


class DeviceNotFoundError(KeyError):
    pass


class DeviceAlreadyExistsError(ValueError):
    pass


class InMemoryDeviceRepository:
    def __init__(self) -> None:
        self._devices: dict[str, DeviceRead] = {}
        self._positions: dict[str, list[DevicePosition]] = {}
        self._lock = RLock()

    def add(self, device: DeviceRead) -> DeviceRead:
        with self._lock:
            if device.device_id in self._devices:
                raise DeviceAlreadyExistsError(device.device_id)
            self._devices[device.device_id] = device
            self._positions[device.device_id] = []
        return device

    def get(self, device_id: str) -> DeviceRead:
        with self._lock:
            device = self._devices.get(device_id)
        if device is None:
            raise DeviceNotFoundError(device_id)
        return device

    def list(self) -> list[DeviceRead]:
        with self._lock:
            return sorted(self._devices.values(), key=lambda device: device.device_id)

    def replace(self, device: DeviceRead) -> DeviceRead:
        self.get(device.device_id)
        with self._lock:
            self._devices[device.device_id] = device
        return device

    def add_position(self, position: DevicePosition) -> DevicePosition:
        self.get(position.device_id)
        with self._lock:
            self._positions[position.device_id].append(position)
        return position

    def record_telemetry(self, sample: Telemetry) -> DeviceRead:
        try:
            current = self.get(sample.device_id)
        except DeviceNotFoundError:
            current = self.add(
                DeviceRead(
                    deviceId=sample.device_id,
                    displayName=sample.device_id,
                    deviceType="simulator" if sample.device_id.startswith("sim-") else "other",
                    registeredAt=sample.occurred_at,
                )
            )

        updated = current.model_copy(
            update={
                "last_seen_at": sample.occurred_at,
                "online": True,
                "location": sample.location,
                "battery_percent": sample.battery_percent,
                "solar_charging": sample.solar_charging,
            }
        )
        self.replace(updated)
        if sample.location is not None and sample.location.valid:
            self.add_position(
                DevicePosition(
                    deviceId=sample.device_id,
                    recordedAt=sample.occurred_at,
                    location=sample.location,
                )
            )
        return updated

    def position_history(self, device_id: str, limit: int = 150) -> list[DevicePosition]:
        self.get(device_id)
        with self._lock:
            return self._positions[device_id][-limit:]

    def clear(self) -> None:
        with self._lock:
            self._devices.clear()
            self._positions.clear()
