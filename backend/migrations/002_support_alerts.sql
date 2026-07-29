CREATE TABLE IF NOT EXISTS support_alerts (
    alert_id UUID PRIMARY KEY,
    incident_id UUID NOT NULL REFERENCES incidents(incident_id) ON DELETE CASCADE,
    target_device_id VARCHAR(80) NOT NULL REFERENCES devices(device_id),
    distance_meters DOUBLE PRECISION NOT NULL CHECK (distance_meters >= 0),
    created_at TIMESTAMPTZ NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    responded_at TIMESTAMPTZ,
    UNIQUE (incident_id, target_device_id),
    CHECK (status IN ('pending', 'checking', 'available', 'unavailable'))
);

CREATE INDEX IF NOT EXISTS ix_support_alerts_incident
    ON support_alerts (incident_id, created_at);
CREATE INDEX IF NOT EXISTS ix_support_alerts_target_status
    ON support_alerts (target_device_id, status);

