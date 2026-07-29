# P0 Architecture

AgriGuard's first milestone is one reproducible safety path:

```text
telemetry -> risk assessment -> suspected -> 10-second confirmation
          -> cancelled | detected -> SOS/control-room event
```

## Boundaries

- The device samples IMU, GPS and power data and keeps a 30-second local buffer.
- The API validates messages and owns the incident state machine.
- The risk engine returns a score, classification and evidence. It never sends SOS by itself.
- The control room consumes the same incident events stored by the API.
- Alcohol and solar features remain auxiliary and cannot block the core incident path.

## P0 quality gates

- A slope alone must not create a confirmed incident.
- A transient impact followed by posture recovery must be cancelled.
- A risky posture plus impact and inactivity must enter confirmation.
- A cancel command during confirmation must be recorded.
- No response before the deadline must create a detected incident.

