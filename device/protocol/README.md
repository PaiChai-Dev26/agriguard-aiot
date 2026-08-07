# Device telemetry protocol

This directory is the contract between the ESP32 firmware and the FastAPI server.
Firmware and frontend changes must use the camelCase field names in
`telemetry.schema.json`.

## Transport

- Development endpoint: `POST /api/v1/telemetry`
- Content type: `application/json`
- Device sampling target: IMU 50 Hz
- Network transmission target: 5 Hz (one payload every 200 ms)
- `occurredAt`: ISO 8601 including a timezone; use UTC when the device can synchronize time
- Retry: retain unsent samples in the device ring buffer and resend oldest first

The server response is a risk result. The device must not treat the risk result as a
confirmed emergency. Incident confirmation and SOS are server policy.

## Units

| Field | Unit |
|---|---|
| `accelX/Y/Z` | g |
| `gyroX/Y/Z` | degrees/second |
| `roll`, `pitch` | degrees |
| `impactG` | g |
| `inactiveSeconds` | seconds |
| `speedKph` | km/h |
| latitude/longitude | WGS84 decimal degrees |

## Missing sensors

- Send `location: null` until GPS has a valid fix.
- Keep `location.valid: false` when coordinates are cached or unreliable.
- Default `batteryPercent` to `100` only in a simulator; firmware should send a measured value.
- `solarCharging` defaults to `false` when the charger state is unavailable.

## Firmware checklist

1. Calibrate the MPU6050 while the platform is stationary.
2. Calculate roll and pitch using the agreed filter.
3. Populate the example payload without renaming fields.
4. Confirm a `200` response from `/api/v1/telemetry`.
5. Test Wi-Fi loss, buffering, reconnection, and ordered retransmission.

