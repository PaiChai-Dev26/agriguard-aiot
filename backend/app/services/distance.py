from math import asin, cos, radians, sin, sqrt

from backend.app.schemas import Location

EARTH_RADIUS_METERS = 6_371_000


def haversine_meters(origin: Location, destination: Location) -> float:
    latitude_delta = radians(destination.latitude - origin.latitude)
    longitude_delta = radians(destination.longitude - origin.longitude)
    origin_latitude = radians(origin.latitude)
    destination_latitude = radians(destination.latitude)

    a = (
        sin(latitude_delta / 2) ** 2
        + cos(origin_latitude)
        * cos(destination_latitude)
        * sin(longitude_delta / 2) ** 2
    )
    return 2 * EARTH_RADIUS_METERS * asin(sqrt(a))


def is_within_radius(origin: Location, destination: Location, radius_meters: float) -> bool:
    if radius_meters < 0:
        raise ValueError("radius must not be negative")
    return haversine_meters(origin, destination) <= radius_meters

