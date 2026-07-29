from simulator.scenarios import generate


def test_scenario_generator_emits_contract_shape() -> None:
    payload = next(generate("rollover", count=1))
    assert payload["type"] == "device.telemetry"
    assert payload["deviceId"]
    assert payload["imu"]["roll"] > 55
    assert payload["location"]["valid"] is True

