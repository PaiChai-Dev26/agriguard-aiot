from datetime import timedelta
from uuid import uuid4

from fastapi import FastAPI

from backend.app.api.incidents import repository as incident_repository
from backend.app.api.incidents import router as incidents_router
from backend.app.config import get_settings
from backend.app.schemas import IncidentRead, RiskResult, Telemetry
from backend.app.services.risk import assess_risk
from backend.app.ws.routes import router as websocket_router

app = FastAPI(title="AgriGuard API", version="0.1.0")
app.include_router(incidents_router)
app.include_router(websocket_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/telemetry", response_model=RiskResult)
def ingest_telemetry(sample: Telemetry) -> RiskResult:
    result = assess_risk(sample)
    if result.classification == "rollover":
        settings = get_settings()
        incident_repository.add(
            IncidentRead(
                id=uuid4(),
                deviceId=sample.device_id,
                occurredAt=sample.occurred_at,
                status="pending_confirmation",
                risk=result,
                location=sample.location,
                confirmationDeadline=sample.occurred_at
                + timedelta(seconds=settings.confirmation_seconds),
            )
        )
    return result
