from datetime import datetime, timezone

from backend.app.schemas import Telemetry
from backend.app.services.risk import assess_rollover_risk


def sample(**overrides) -> Telemetry:
    data = dict(
        device_id="test-001",
        occurred_at=datetime.now(timezone.utc),
        ax=0,
        ay=0,
        az=1,
        gx=0,
        gy=0,
        gz=0,
        roll=0,
        pitch=0,
        speed_kmh=4,
        motion_rms=0.2,
    )
    data.update(overrides)
    return Telemetry(**data)


def test_normal_and_slope_do_not_become_rollover_candidates() -> None:
    assert assess_rollover_risk(sample()).label == "normal"
    slope = assess_rollover_risk(sample(roll=25))
    assert slope.label == "slope"
    assert slope.score < 0.7


def test_vibration_is_not_rollover_without_dangerous_tilt() -> None:
    risk = assess_rollover_risk(sample(motion_rms=1.2, gx=90))
    assert risk.label == "vibration"
    assert risk.score < 0.7


def test_rollover_combines_tilt_impact_stillness_and_stop() -> None:
    risk = assess_rollover_risk(
        sample(roll=72, ax=1.8, az=0.2, gx=220, motion_rms=0.05, speed_kmh=0)
    )
    assert risk.label == "rollover_candidate"
    assert risk.score >= 0.9
    assert "dangerous_tilt" in risk.reasons

