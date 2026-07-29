from backend.app.schemas import IncidentRead, SosPayload


class SosUnavailableError(ValueError):
    pass


def create_sos_payload(incident: IncidentRead) -> SosPayload:
    if incident.status not in {"detected", "acknowledged", "dispatched"}:
        raise SosUnavailableError("incident is not confirmed")
    if incident.location is None or not incident.location.valid:
        raise SosUnavailableError("valid incident location is required")

    summary = (
        f"AgriGuard 전도 사고 의심: 장치 {incident.device_id}, "
        f"위험도 {incident.risk.risk_score:.0%}, "
        f"위치 {incident.location.latitude:.6f}, {incident.location.longitude:.6f}"
    )
    return SosPayload(
        incidentId=incident.id,
        deviceId=incident.device_id,
        occurredAt=incident.occurred_at,
        location=incident.location,
        riskScore=incident.risk.risk_score,
        summary=summary,
    )

