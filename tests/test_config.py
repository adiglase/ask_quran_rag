from app.config import Settings


def test_settings_defaults_without_environment(monkeypatch) -> None:
    monkeypatch.delenv("ASK_QURAN_ENVIRONMENT", raising=False)

    settings = Settings()

    assert settings.app_name == "Ask Quran RAG"
    assert settings.environment == "local"


def test_tests_default_to_test_environment() -> None:
    settings = Settings()

    assert settings.environment == "test"


def test_settings_read_prefixed_environment(monkeypatch) -> None:
    monkeypatch.setenv("ASK_QURAN_APP_NAME", "Custom Ask Quran")
    monkeypatch.setenv("ASK_QURAN_ENVIRONMENT", "test")

    settings = Settings()

    assert settings.app_name == "Custom Ask Quran"
    assert settings.environment == "test"
