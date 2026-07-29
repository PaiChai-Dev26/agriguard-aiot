from sqlalchemy import text

from backend.app.db import build_engine, build_session_factory


def test_sqlite_engine_and_session_factory() -> None:
    engine = build_engine("sqlite+pysqlite:///:memory:")
    factory = build_session_factory(engine)
    with factory() as session:
        assert session.scalar(text("SELECT 1")) == 1


def test_pool_pre_ping_is_enabled() -> None:
    engine = build_engine("sqlite+pysqlite:///:memory:")
    assert engine.pool._pre_ping is True

