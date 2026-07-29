CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS devices (
    device_id VARCHAR(80) PRIMARY KEY,
    display_name VARCHAR(100) NOT NULL,
    device_type VARCHAR(20) NOT NULL,
    registered_at TIMESTAMPTZ NOT NULL,
    last_seen_at TIMESTAMPTZ,
    online BOOLEAN NOT NULL DEFAULT FALSE,
    battery_percent SMALLINT CHECK (battery_percent BETWEEN 0 AND 100),
    solar_charging BOOLEAN,
    last_location GEOGRAPHY(POINT, 4326)
);

CREATE TABLE IF NOT EXISTS telemetry (
    id BIGSERIAL PRIMARY KEY,
    device_id VARCHAR(80) NOT NULL REFERENCES devices(device_id),
    occurred_at TIMESTAMPTZ NOT NULL,
    accel_x DOUBLE PRECISION NOT NULL,
    accel_y DOUBLE PRECISION NOT NULL,
    accel_z DOUBLE PRECISION NOT NULL,
    gyro_x DOUBLE PRECISION NOT NULL,
    gyro_y DOUBLE PRECISION NOT NULL,
    gyro_z DOUBLE PRECISION NOT NULL,
    roll DOUBLE PRECISION NOT NULL,
    pitch DOUBLE PRECISION NOT NULL,
    impact_g DOUBLE PRECISION NOT NULL,
    inactive_seconds DOUBLE PRECISION NOT NULL,
    speed_kph DOUBLE PRECISION,
    location GEOGRAPHY(POINT, 4326),
    battery_percent SMALLINT CHECK (battery_percent BETWEEN 0 AND 100),
    solar_charging BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS ix_telemetry_device_occurred
    ON telemetry (device_id, occurred_at DESC);
CREATE INDEX IF NOT EXISTS ix_telemetry_location
    ON telemetry USING GIST (location);

CREATE TABLE IF NOT EXISTS incidents (
    incident_id UUID PRIMARY KEY,
    device_id VARCHAR(80) NOT NULL REFERENCES devices(device_id),
    occurred_at TIMESTAMPTZ NOT NULL,
    status VARCHAR(30) NOT NULL,
    confirmation_deadline TIMESTAMPTZ,
    classification VARCHAR(20) NOT NULL,
    risk_score DOUBLE PRECISION NOT NULL CHECK (risk_score BETWEEN 0 AND 1),
    evidence JSONB NOT NULL DEFAULT '[]'::jsonb,
    model_version VARCHAR(50) NOT NULL,
    location GEOGRAPHY(POINT, 4326)
);

CREATE INDEX IF NOT EXISTS ix_incidents_status_occurred
    ON incidents (status, occurred_at DESC);
CREATE INDEX IF NOT EXISTS ix_incidents_location
    ON incidents USING GIST (location);

