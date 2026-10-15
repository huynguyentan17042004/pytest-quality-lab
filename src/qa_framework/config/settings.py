from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType
from typing import Any
from urllib.parse import urlparse

from qa_framework.exceptions import ConfigurationError


@dataclass(frozen=True, slots=True)
class Settings:
    environment: str = "local"
    api_base_url: str = "http://127.0.0.1"
    ui_base_url: str = "file:///"
    browser: str = "chrome"
    timeout: float = 10.0
    headless: bool = True
    retry_count: int = 0
    report: Mapping[str, Any] = field(default_factory=lambda: MappingProxyType({}))
    project_root: Path = field(default_factory=lambda: Path.cwd())

    def __post_init__(self) -> None:
        if not self.environment.strip():
            raise ConfigurationError("environment must not be empty")
        if self.browser not in {"chrome", "firefox"}:
            raise ConfigurationError(f"browser must be chrome or firefox, got {self.browser!r}")
        if self.timeout <= 0 or self.timeout > 300:
            raise ConfigurationError("timeout must be greater than 0 and at most 300 seconds")
        if self.retry_count < 0 or self.retry_count > 5:
            raise ConfigurationError("retry_count must be between 0 and 5")
        for name in ("api_base_url", "ui_base_url"):
            value = getattr(self, name)
            parsed = urlparse(value)
            if parsed.scheme not in {"http", "https", "file"}:
                raise ConfigurationError(f"{name} must use http, https or file scheme")
        object.__setattr__(self, "report", MappingProxyType(dict(self.report)))
        object.__setattr__(self, "project_root", Path(self.project_root).resolve())
