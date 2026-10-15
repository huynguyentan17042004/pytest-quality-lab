from pathlib import Path

import pytest

from qa_framework.config.environment_loader import load_settings
from qa_framework.config.settings import Settings
from qa_framework.exceptions import ConfigurationError

pytestmark = [pytest.mark.framework, pytest.mark.unit]


def test_settings_are_immutable():
    settings = Settings()
    with pytest.raises((AttributeError, TypeError)):
        settings.timeout = 99


@pytest.mark.parametrize("timeout", [0, -1, 301])
def test_invalid_timeout_has_field_diagnostic(timeout):
    with pytest.raises(ConfigurationError, match="timeout"):
        Settings(timeout=timeout)


def test_precedence_cli_over_environment_over_toml(tmp_path: Path):
    config_dir = tmp_path / "configs" / "environments"
    config_dir.mkdir(parents=True)
    (config_dir / "local.toml").write_text(
        'api_base_url="http://toml.test"\nui_base_url="http://ui.test"\nbrowser="chrome"\ntimeout=5\nheadless=true\nretry_count=0\n',
        encoding="utf-8",
    )
    settings = load_settings(tmp_path, environ={"QA_TIMEOUT": "7"}, cli_overrides={"timeout": 9})
    assert settings.timeout == 9
    assert settings.api_base_url == "http://toml.test"


def test_missing_environment_file_is_clear(tmp_path):
    with pytest.raises(ConfigurationError, match="environment config not found"):
        load_settings(tmp_path, "missing", environ={})
