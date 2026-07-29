from collections.abc import Iterator
from datetime import datetime, timedelta, timezone


SCENARIOS = {
    "normal": {"roll": 2.0, "pitch": 1.0, "impactG": 0.1, "inactiveSeconds": 0.0},
    "slope": {"roll": 25.0, "pitch": 4.0, "impactG": 0.2, "inactiveSeconds": 0.0},
    "vibration": {"roll": 8.0, "pitch": 5.0, "impactG": 2.5, "inactiveSeconds": 0.2},
    "rollover": {"roll": 74.0, "pitch": 9.0, "impactG": 2.9, "inactiveSeconds": 5.0},
}


def generate(name: str, count: int = 10) -> Iterator[dict]:
    if name not in SCENARIOS:
        raise ValueError(f"unknown scenario: {name}")
    started = datetime.now(timezone.utc)
    scenario = SCENARIOS[name]
    for index in range(count):
        yield {
            "type": "device.telemetry",
            "deviceId": "sim-tractor-001",
            "occurredAt": (started + timedelta(milliseconds=200 * index)).isoformat(),
            "imu": {
                "accelX": 0.02,
                "accelY": 0.91,
                "accelZ": 0.12,
                "gyroX": 1.2,
                "gyroY": 0.5,
                "gyroZ": 0.2,
                "roll": scenario["roll"],
                "pitch": scenario["pitch"],
            },
            "location": {
                "latitude": 36.3012 + index * 0.00001,
                "longitude": 127.5874,
                "speedKph": 0.0 if name == "rollover" else 4.0,
                "valid": True,
            },
            "impactG": scenario["impactG"],
            "inactiveSeconds": scenario["inactiveSeconds"],
            "batteryPercent": 78,
            "solarCharging": True,
        }

