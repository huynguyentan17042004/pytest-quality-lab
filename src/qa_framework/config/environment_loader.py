from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import tomllib
from dotenv import dotenv_values

from qa_framework.config.settings import Settings
from qa_framework.exceptions import ConfigurationError

ENV_MAP = {
    "QA_API_BASE_URL": "api_base_url",
    "QA_UI_BASE_URL": "ui_base_url",
    "QA_BROWSER": "browser",
    "QA_TIMEOUT": "timeout",
    "QA_HEADLESS": "headless",
    "QA_RETRY_COUNT": "retry_count",
}


def _convert(name: str, value: Any) -> Any:
    if name == "timeout":
        return float(value)
    if name == "retry_count":
        return int(value)
    if name == "headless" and isinstance(value, str):
        lowered = value.lower()
        if lowered not in {"1", "0", "true", "false", "yes", "no"}:
            raise ConfigurationError(f"headless has invalid boolean value {value!r}")
        return lowered in {"1", "true", "yes"}
    return value


def load_settings(
    project_root: str | Path,
    environment: str = "local",
    cli_overrides: Mapping[str, Any] | None = None,
    environ: Mapping[str, str] | None = None,
) -> Settings:
    root = Path(project_root).resolve()
    config_path = root / "configs" / "environments" / f"{environment}.toml"
    if not config_path.is_file():
        raise ConfigurationError(f"environment config not found: {config_path}")
    try:
        with config_path.open("rb") as stream:
            merged: dict[str, Any] = tomllib.load(stream)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise ConfigurationError(f"cannot load environment config: {config_path}") from exc

    merged["environment"] = environment
    dotenv_data = dotenv_values(root / ".env")
    source_env = dict(os.environ if environ is None else environ)
    for env_name, field_name in ENV_MAP.items():
        value = source_env.get(env_name, dotenv_data.get(env_name))
        if value not in (None, ""):
            merged[field_name] = _convert(field_name, value)
    for field_name, value in (cli_overrides or {}).items():
        if value is not None:
            merged[field_name] = _convert(field_name, value)
    merged["project_root"] = root
    try:
        return Settings(**merged)
    except TypeError as exc:
        raise ConfigurationError(f"unknown setting in {config_path}: {exc}") from exc
