import pytest

from backend.app.schemas import Location
from backend.app.services.distance import haversine_meters, is_within_radius


def test_same_location_has_zero_distance() -> None:
    location = Location(latitude=36.3012, longitude=127.5874)
    assert haversine_meters(location, location) == 0


def test_known_latitude_delta_is_about_one_kilometer() -> None:
    origin = Location(latitude=36.3012, longitude=127.5874)
    destination = Location(latitude=36.3102, longitude=127.5874)
    assert haversine_meters(origin, destination) == pytest.approx(1000.8, abs=2)


def test_radius_boundary() -> None:
    origin = Location(latitude=36.3012, longitude=127.5874)
    near = Location(latitude=36.305, longitude=127.5874)
    far = Location(latitude=36.32, longitude=127.5874)
    assert is_within_radius(origin, near, 1000) is True
    assert is_within_radius(origin, far, 1000) is False


def test_negative_radius_is_rejected() -> None:
    location = Location(latitude=36.3012, longitude=127.5874)
    with pytest.raises(ValueError):
        is_within_radius(location, location, -1)

