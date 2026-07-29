from backend.app.schemas import RiskResult, Telemetry


def assess_risk(sample: Telemetry) -> RiskResult:
    """Transparent P0 baseline; ML can replace this behind the same contract."""
    tilt = max(abs(sample.imu.roll), abs(sample.imu.pitch))
    evidence: list[str] = []
    score = 0.0

    if tilt >= 55:
        evidence.append("dangerous_tilt")
        score += 0.45
    elif tilt >= 20:
        evidence.append("slope")
        score += 0.15

    if sample.impact_g >= 2.2:
        evidence.append("impact")
        score += 0.3
    if sample.inactive_seconds >= 3:
        evidence.append("inactivity")
        score += 0.25

    if {"dangerous_tilt", "impact", "inactivity"} <= set(evidence):
        classification = "rollover"
    elif "impact" in evidence and sample.inactive_seconds < 1:
        classification = "vibration"
    elif "slope" in evidence or "dangerous_tilt" in evidence:
        classification = "slope"
    else:
        classification = "normal"

    return RiskResult(
        classification=classification,
        riskScore=min(score, 1.0),
        evidence=evidence,
        modelVersion="rules-v1",
    )

