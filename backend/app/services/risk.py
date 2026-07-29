import math

from backend.app.schemas import RiskAssessment, Telemetry


def assess_rollover_risk(sample: Telemetry) -> RiskAssessment:
    """Transparent baseline to be replaced by the AI team's model adapter."""
    tilt = max(abs(sample.roll), abs(sample.pitch))
    acceleration = math.sqrt(sample.ax**2 + sample.ay**2 + sample.az**2)
    impact = abs(acceleration - 1.0)

    score = 0.0
    reasons: list[str] = []

    if tilt >= 55:
        score += 0.45
        reasons.append("dangerous_tilt")
    elif tilt >= 35:
        score += 0.2
        reasons.append("elevated_tilt")

    if impact >= 0.8 or max(abs(sample.gx), abs(sample.gy), abs(sample.gz)) >= 180:
        score += 0.3
        reasons.append("impact_or_rotation_peak")

    if tilt >= 55 and sample.motion_rms <= 0.12:
        score += 0.2
        reasons.append("abnormal_pose_without_motion")

    if tilt >= 55 and sample.speed_kmh <= 1.0:
        score += 0.05
        reasons.append("stopped_after_tilt")

    score = min(score, 1.0)
    if score >= 0.7:
        label = "rollover_candidate"
    elif sample.motion_rms >= 0.8 and tilt < 35:
        label = "vibration"
    elif tilt >= 20:
        label = "slope"
    else:
        label = "normal"

    return RiskAssessment(score=score, label=label, reasons=reasons)

