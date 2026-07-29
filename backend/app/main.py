import asyncio
from contextlib import asynccontextmanager, suppress
from datetime import timedelta
from uuid import uuid4

from fastapi import FastAPI

from backend.app.api.devices import router as devices_router
from backend.app.api.incidents import repository as incident_repository
from backend.app.api.incidents import router as incidents_router
from backend.app.config import get_settings
from backend.app.schemas import IncidentRead, RiskResult, Telemetry
from backend.app.services.confirmation import confirm_due_incidents
from backend.app.services.risk import assess_risk
from backend.app.ws.manager import control_room_manager
from backend.app.ws.routes import router as websocket_router


async def _confirmation_monitor() -> None:
    while True:
        await confirm_due_incidents(incident_repository, control_room_manager)
        await asyncio.sleep(0.25)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(_confirmation_monitor(), name="incident-confirmation-monitor")
    app.state.confirmation_task = task
    yield
    task.cancel()
    with suppress(asyncio.CancelledError):
        await task


app = FastAPI(title="AgriGuard API", version="0.1.0", lifespan=lifespan)
app.include_router(devices_router)
app.include_router(incidents_router)
app.include_router(websocket_router)


@app.get("/health")
def health() -> dict[str, str]:
    monitor = getattr(app.state, "confirmation_task", None)
    return {
        "status": "ok",
        "confirmationMonitor": "running" if monitor and not monitor.done() else "stopped",
    }


@app.post("/api/v1/telemetry", response_model=RiskResult)
async def ingest_telemetry(sample: Telemetry) -> RiskResult:
    result = assess_risk(sample)
    await control_room_manager.broadcast(
        {
            "type": "device.telemetry",
            "deviceId": sample.device_id,
            "occurredAt": sample.occurred_at.isoformat(),
            "risk": result.model_dump(by_alias=True),
        }
    )
    if result.classification == "rollover":
        settings = get_settings()
        incident = incident_repository.add(
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
        await control_room_manager.broadcast(
            {
                "type": "incident.suspected",
                "incident": incident.model_dump(mode="json", by_alias=True),
            }
        )
    return result
