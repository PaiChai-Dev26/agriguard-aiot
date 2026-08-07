import json
from pathlib import Path

from backend.app.schemas import Telemetry


ROOT = Path(__file__).parents[1]
PROTOCOL = ROOT / "device" / "protocol"


def test_committed_schema_tracks_required_telemetry_fields() -> None:
    committed = json.loads((PROTOCOL / "telemetry.schema.json").read_text(encoding="utf-8"))
    runtime = Telemetry.model_json_schema(by_alias=True)

    assert set(committed["required"]) == set(runtime["required"])
    assert committed["properties"]["type"]["const"] == "device.telemetry"
    assert committed["properties"]["location"]["oneOf"][1]["properties"]["latitude"]["minimum"] == -90
    assert committed["properties"]["location"]["oneOf"][1]["properties"]["latitude"]["maximum"] == 90


def test_firmware_example_is_accepted_by_fastapi_model() -> None:
    payload = json.loads(
        (PROTOCOL / "examples" / "telemetry.json").read_text(encoding="utf-8")
    )

    telemetry = Telemetry.model_validate(payload)

    assert telemetry.device_id == "tractor-001"
    assert telemetry.imu.roll == 76.0
    assert telemetry.location is not None
    assert telemetry.location.valid is True


def test_firmware_example_uses_wire_aliases() -> None:
    payload = json.loads(
        (PROTOCOL / "examples" / "telemetry.json").read_text(encoding="utf-8")
    )
    round_trip = Telemetry.model_validate(payload).model_dump(mode="json", by_alias=True)

    assert round_trip["deviceId"] == payload["deviceId"]
    assert round_trip["occurredAt"] == payload["occurredAt"]
    assert round_trip["imu"] == payload["imu"]

