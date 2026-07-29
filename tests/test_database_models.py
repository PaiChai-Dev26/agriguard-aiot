from datetime import datetime, timezone

from sqlalchemy import inspect
from sqlalchemy.orm import Session

from backend.app.db import build_engine
from backend.app.models.database import Base, DeviceRow


def test_metadata_creates_core_tables() -> None:
    engine = build_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    assert set(inspect(engine).get_table_names()) == {
        "devices",
        "incidents",
        "support_alerts",
        "telemetry",
    }


def test_device_row_round_trip() -> None:
    engine = build_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        session.add(
            DeviceRow(
                device_id="tractor-001",
                display_name="1번 트랙터",
                device_type="tractor",
                registered_at=datetime.now(timezone.utc),
                online=False,
            )
        )
        session.commit()
        assert session.get(DeviceRow, "tractor-001").display_name == "1번 트랙터"

