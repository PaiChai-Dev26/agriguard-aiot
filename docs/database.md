# Database

PostgreSQL 17 with PostGIS stores devices, telemetry, incidents and geographic
positions. On a fresh Docker volume, SQL files in `backend/migrations` run in
lexical order.

## Local startup

```bash
docker compose up -d db
docker compose ps
```

The initial schema uses `GEOGRAPHY(POINT, 4326)` so distance queries are in
meters:

```sql
SELECT device_id
FROM devices
WHERE online = TRUE
  AND last_location IS NOT NULL
  AND ST_DWithin(
        last_location,
        ST_SetSRID(ST_MakePoint(:longitude, :latitude), 4326)::geography,
        1000
      );
```

Migrations are immutable after merge. Add a new numbered file for each schema
change rather than editing an already deployed migration.

