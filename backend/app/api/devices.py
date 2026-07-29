from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status

from backend.app.repositories.devices import (
    DeviceAlreadyExistsError,
    DeviceNotFoundError,
    InMemoryDeviceRepository,
)
from backend.app.schemas import DevicePosition, DeviceRead, DeviceRegister

router = APIRouter(prefix="/api/v1/devices", tags=["devices"])
repository = InMemoryDeviceRepository()


def _get_or_404(device_id: str) -> DeviceRead:
    try:
        return repository.get(device_id)
    except DeviceNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="device not found") from error


@router.post("/register", response_model=DeviceRead, status_code=status.HTTP_201_CREATED)
def register_device(command: DeviceRegister) -> DeviceRead:
    device = DeviceRead(
        **command.model_dump(by_alias=True),
        registeredAt=datetime.now(timezone.utc),
    )
    try:
        return repository.add(device)
    except DeviceAlreadyExistsError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="device already exists") from error


@router.get("", response_model=list[DeviceRead])
def list_devices() -> list[DeviceRead]:
    return repository.list()


@router.get("/{device_id}", response_model=DeviceRead)
def get_device(device_id: str) -> DeviceRead:
    return _get_or_404(device_id)


@router.get("/{device_id}/positions", response_model=list[DevicePosition])
def get_device_positions(device_id: str, limit: int = 150) -> list[DevicePosition]:
    if limit < 1 or limit > 1000:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="limit must be between 1 and 1000",
        )
    _get_or_404(device_id)
    return repository.position_history(device_id, limit=limit)
