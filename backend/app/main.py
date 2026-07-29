import os
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

from backend.app.schemas import IncidentEvent, Telemetry, TelemetryResult
from backend.app.services.incident import IncidentStateMachine
from backend.app.services.risk import assess_rollover_risk
from backend.app.ws.manager import ConnectionManager

app = FastAPI(title="AgriGuard AIoT API", version="0.1.0")
manager = ConnectionManager()
state_machine = IncidentStateMachine(
    confirmation_seconds=float(os.getenv("CONFIRMATION_SECONDS", "10"))
)
latest_by_device: dict[str, TelemetryResult] = {}
events: list[IncidentEvent] = []


@app.get("/")
async def control_room() -> FileResponse:
    return FileResponse(Path(__file__).parent / "static" / "index.html")


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/api/v1/telemetry", response_model=TelemetryResult)
async def ingest_telemetry(sample: Telemetry) -> TelemetryResult:
    risk = assess_rollover_risk(sample)
    state, remaining, event = state_machine.process(sample, risk)
    result = TelemetryResult(
        telemetry=sample,
        risk=risk,
        incident_state=state,
        confirmation_remaining_seconds=remaining,
    )
    latest_by_device[sample.device_id] = result
    if event:
        events.append(event)

    await manager.broadcast(
        {
            "type": "telemetry.processed",
            "data": result.model_dump(mode="json"),
            "event": event.model_dump(mode="json") if event else None,
        }
    )
    return result


@app.get("/api/v1/devices")
async def list_devices() -> list[TelemetryResult]:
    return list(latest_by_device.values())


@app.get("/api/v1/incidents")
async def list_incidents() -> list[IncidentEvent]:
    return events


@app.post("/api/v1/devices/{device_id}/cancel", response_model=IncidentEvent)
async def cancel_incident(device_id: str) -> IncidentEvent:
    event = state_machine.cancel(device_id, datetime.now(timezone.utc))
    if event is None:
        raise HTTPException(status_code=409, detail="No pending incident to cancel")
    events.append(event)
    await manager.broadcast({"type": event.type, "event": event.model_dump(mode="json")})
    return event


@app.post("/api/v1/devices/{device_id}/reset", status_code=204)
async def reset_incident(device_id: str) -> None:
    state_machine.reset(device_id)


@app.websocket("/ws/control-room")
async def control_room_ws(websocket: WebSocket) -> None:
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

