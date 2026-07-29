from fastapi import FastAPI

from backend.app.api.incidents import router as incidents_router
from backend.app.schemas import RiskResult, Telemetry
from backend.app.services.risk import assess_risk

app = FastAPI(title="AgriGuard API", version="0.1.0")
app.include_router(incidents_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/v1/telemetry", response_model=RiskResult)
def ingest_telemetry(sample: Telemetry) -> RiskResult:
    return assess_risk(sample)
