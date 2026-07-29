from datetime import datetime, timezone

from backend.app.schemas import ImuSample, Telemetry
from backend.app.services.risk import assess_risk


def sample(**overrides: float) -> Telemetry:
    values = {"roll": 0.0, "pitch": 0.0, "impact_g": 0.0, "inactive_seconds": 0.0}
    values.update(overrides)
    return Telemetry(
        deviceId="tractor-001",
        occurredAt=datetime.now(timezone.utc),
        imu=ImuSample(
            accelX=0, accelY=0, accelZ=1,
            gyroX=0, gyroY=0, gyroZ=0,
            roll=values["roll"], pitch=values["pitch"],
        ),
        impactG=values["impact_g"],
        inactiveSeconds=values["inactive_seconds"],
    )


def test_slope_alone_is_not_rollover() -> None:
    result = assess_risk(sample(roll=30))
    assert result.classification == "slope"
    assert result.risk_score < 0.7


def test_rollover_requires_combined_evidence() -> None:
    result = assess_risk(sample(roll=70, impact_g=2.8, inactive_seconds=5))
    assert result.classification == "rollover"
    assert result.risk_score >= 0.9


def test_transient_impact_is_vibration() -> None:
    result = assess_risk(sample(impact_g=2.5, inactive_seconds=0.2))
    assert result.classification == "vibration"

