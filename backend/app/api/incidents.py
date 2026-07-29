from uuid import UUID

from fastapi import APIRouter, HTTPException, status

from backend.app.config import get_settings
from backend.app.dependencies import (
    device_repository,
    incident_repository as repository,
    support_alert_repository,
)
from backend.app.repositories.incidents import IncidentNotFoundError
from backend.app.schemas import (
    CancelIncident,
    IncidentRead,
    IncidentStatusUpdate,
    NearbyDevice,
    SosPayload,
    SupportAlert,
    SupportResponse,
)
from backend.app.services.nearby import find_nearby_devices
from backend.app.services.sos import SosUnavailableError, create_sos_payload
from backend.app.services.support import create_support_alerts, respond_to_alert
from backend.app.ws.manager import control_room_manager

router = APIRouter(prefix="/api/v1/incidents", tags=["incidents"])

ALLOWED_TRANSITIONS = {
    "detected": {"acknowledged", "resolved"},
    "acknowledged": {"dispatched", "resolved"},
    "dispatched": {"resolved"},
}


def _get_or_404(incident_id: UUID) -> IncidentRead:
    try:
        return repository.get(incident_id)
    except IncidentNotFoundError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="incident not found") from error


@router.get("", response_model=list[IncidentRead])
def list_incidents() -> list[IncidentRead]:
    return repository.list()


@router.get("/{incident_id}", response_model=IncidentRead)
def get_incident(incident_id: UUID) -> IncidentRead:
    return _get_or_404(incident_id)


@router.post("/{incident_id}/cancel", response_model=IncidentRead)
def cancel_incident(incident_id: UUID, command: CancelIncident) -> IncidentRead:
    incident = _get_or_404(incident_id)
    if incident.status not in {"suspected", "pending_confirmation"}:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="incident cannot be cancelled")
    updated = incident.model_copy(update={"status": "cancelled"})
    return repository.replace(updated)


@router.patch("/{incident_id}/status", response_model=IncidentRead)
def update_incident_status(incident_id: UUID, command: IncidentStatusUpdate) -> IncidentRead:
    incident = _get_or_404(incident_id)
    if command.status not in ALLOWED_TRANSITIONS.get(incident.status, set()):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="invalid incident transition")
    updated = incident.model_copy(update={"status": command.status})
    return repository.replace(updated)


@router.get("/{incident_id}/sos", response_model=SosPayload)
def get_incident_sos(incident_id: UUID) -> SosPayload:
    incident = _get_or_404(incident_id)
    try:
        return create_sos_payload(incident)
    except SosUnavailableError as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error


@router.get("/{incident_id}/nearby-devices", response_model=list[NearbyDevice])
def get_nearby_devices(incident_id: UUID) -> list[NearbyDevice]:
    incident = _get_or_404(incident_id)
    if incident.location is None or not incident.location.valid:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="valid incident location is required",
        )
    return find_nearby_devices(
        device_repository.list(),
        source_device_id=incident.device_id,
        incident_location=incident.location,
        radius_meters=get_settings().nearby_radius_meters,
    )


@router.post(
    "/{incident_id}/nearby-alert",
    response_model=list[SupportAlert],
    status_code=status.HTTP_201_CREATED,
)
async def send_nearby_alert(incident_id: UUID) -> list[SupportAlert]:
    incident = _get_or_404(incident_id)
    nearby = get_nearby_devices(incident_id)
    if not nearby:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="no eligible nearby devices")
    try:
        alerts = create_support_alerts(support_alert_repository, incident.id, nearby)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="support alerts already sent",
        ) from error
    for alert in alerts:
        await control_room_manager.broadcast(
            {
                "type": "incident.nearby",
                "alert": alert.model_dump(mode="json", by_alias=True),
            }
        )
    return alerts


@router.get("/{incident_id}/support-alerts", response_model=list[SupportAlert])
def list_support_alerts(incident_id: UUID) -> list[SupportAlert]:
    _get_or_404(incident_id)
    return support_alert_repository.for_incident(incident_id)


@router.post("/{incident_id}/support-response", response_model=SupportAlert)
async def submit_support_response(
    incident_id: UUID,
    alert_id: UUID,
    command: SupportResponse,
) -> SupportAlert:
    _get_or_404(incident_id)
    try:
        alert = support_alert_repository.get(alert_id)
        if alert.incident_id != incident_id:
            raise ValueError("alert does not belong to incident")
        updated = respond_to_alert(support_alert_repository, alert_id, command.status)
    except (KeyError, ValueError) as error:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(error)) from error
    await control_room_manager.broadcast(
        {
            "type": "incident.support_response",
            "alert": updated.model_dump(mode="json", by_alias=True),
        }
    )
    return updated
