from pathlib import Path


MIGRATIONS = Path(__file__).parents[1] / "backend" / "migrations"


def test_migration_names_are_ordered_and_unique() -> None:
    names = [path.name for path in sorted(MIGRATIONS.glob("*.sql"))]
    prefixes = [name.split("_", 1)[0] for name in names]
    assert names == sorted(names)
    assert len(prefixes) == len(set(prefixes))


def test_initial_migration_enables_postgis() -> None:
    sql = (MIGRATIONS / "001_initial_schema.sql").read_text(encoding="utf-8")
    assert "CREATE EXTENSION IF NOT EXISTS postgis" in sql
    assert "GEOGRAPHY(POINT, 4326)" in sql


def test_support_alert_statuses_match_domain_contract() -> None:
    sql = (MIGRATIONS / "002_support_alerts.sql").read_text(encoding="utf-8")
    for status in ("pending", "checking", "available", "unavailable"):
        assert f"'{status}'" in sql

