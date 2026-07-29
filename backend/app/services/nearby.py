from datetime import datetime, timedelta, timezone

from backend.app.schemas import DeviceRead, Location, NearbyDevice
from backend.app.services.distance import haversine_meters


def find_nearby_devices(
    devices: list[DeviceRead],
    *,
    source_device_id: str,
    incident_location: Location,
    now: datetime | None = None,
    radius_meters: float = 1000,
    max_location_age: timedelta = timedelta(minutes=2),
    max_speed_kph: float = 20,
) -> list[NearbyDevice]:
    now = now or datetime.now(timezone.utc)
    matches: list[NearbyDevice] = []

    for device in devices:
        if device.device_id == source_device_id or not device.online:
            continue
        if device.location is None or not device.location.valid:
            continue
        if device.last_seen_at is None or now - device.last_seen_at > max_location_age:
            continue
        if device.location.speed_kph > max_speed_kph:
            continue
        distance = haversine_meters(incident_location, device.location)
        if distance <= radius_meters:
            matches.append(NearbyDevice(device=device, distanceMeters=round(distance, 1)))

    return sorted(matches, key=lambda match: match.distance_meters)

