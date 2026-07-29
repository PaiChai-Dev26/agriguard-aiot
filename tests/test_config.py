from backend.app.config import Settings


def test_settings_have_safe_p0_defaults() -> None:
    settings = Settings()
    assert settings.confirmation_seconds == 10
    assert settings.nearby_radius_meters == 1000


def test_settings_accept_prefixed_environment(monkeypatch) -> None:
    monkeypatch.setenv("AGRIGUARD_CONFIRMATION_SECONDS", "12")
    assert Settings().confirmation_seconds == 12

