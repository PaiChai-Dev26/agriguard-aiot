from __future__ import annotations

from threading import RLock

from backend.app.schemas import DevicePosition, DeviceRead


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

    def position_history(self, device_id: str, limit: int = 150) -> list[DevicePosition]:
        self.get(device_id)
        with self._lock:
            return self._positions[device_id][-limit:]

    def clear(self) -> None:
        with self._lock:
            self._devices.clear()
            self._positions.clear()

