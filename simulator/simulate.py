import argparse
import asyncio
from datetime import datetime, timezone

import httpx


SCENARIOS = {
    "normal": dict(roll=2, pitch=3, ax=0.02, ay=0.01, az=1.0, gx=2, gy=1, gz=3, motion_rms=0.2, speed_kmh=6),
    "slope": dict(roll=25, pitch=6, ax=0.35, ay=0.02, az=0.94, gx=3, gy=2, gz=2, motion_rms=0.2, speed_kmh=3),
    "vibration": dict(roll=5, pitch=4, ax=0.3, ay=0.25, az=1.2, gx=45, gy=35, gz=40, motion_rms=1.1, speed_kmh=4),
    "rollover": dict(roll=72, pitch=15, ax=1.8, ay=0.4, az=0.2, gx=220, gy=40, gz=15, motion_rms=0.05, speed_kmh=0),
}


async def run(server: str, device_id: str, scenario: str, count: int, interval: float) -> None:
    async with httpx.AsyncClient(base_url=server, timeout=5) as client:
        for index in range(count):
            payload = {
                "device_id": device_id,
                "occurred_at": datetime.now(timezone.utc).isoformat(),
                "location": {"latitude": 36.3012, "longitude": 127.5874, "accuracy_m": 5},
                "battery_percent": 78,
                **SCENARIOS[scenario],
            }
            response = await client.post("/api/v1/telemetry", json=payload)
            response.raise_for_status()
            result = response.json()
            print(
                f"{index + 1:02d} {scenario:<9} "
                f"risk={result['risk']['score']:.2f} state={result['incident_state']}"
            )
            await asyncio.sleep(interval)


def main() -> None:
    parser = argparse.ArgumentParser(description="AgriGuard virtual IMU/GPS device")
    parser.add_argument("scenario", choices=SCENARIOS)
    parser.add_argument("--server", default="http://localhost:8000")
    parser.add_argument("--device-id", default="sim-tractor-001")
    parser.add_argument("--count", type=int, default=12)
    parser.add_argument("--interval", type=float, default=1)
    args = parser.parse_args()
    asyncio.run(run(args.server, args.device_id, args.scenario, args.count, args.interval))


if __name__ == "__main__":
    main()

