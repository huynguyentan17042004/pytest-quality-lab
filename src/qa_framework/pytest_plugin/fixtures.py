from __future__ import annotations

import os
from dataclasses import dataclass

import pytest
import requests

from qa_framework.config import EnvironmentSandbox, SecretValue
from qa_framework.exceptions import ConfigurationError
from qa_framework.testdata import ResourceTracker
from qa_framework.web import DriverFactory


@dataclass(frozen=True, slots=True)
class DemoCredentials:
    password: SecretValue


@pytest.fixture
def settings(request):
    return request.config._qa_settings


@pytest.fixture
def run_context(request):
    return request.config._qa_run_context


@pytest.fixture
def api_session():
    session = requests.Session()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def resource_tracker():
    tracker = ResourceTracker()
    yield tracker
    errors = tracker.cleanup()
    if errors:
        details = "; ".join(f"{type(error).__name__}: {error}" for error in errors)
        raise RuntimeError(f"resource cleanup failures: {details}") from errors[0]


@pytest.fixture
def isolated_env():
    with EnvironmentSandbox() as sandbox:
        yield sandbox


@pytest.fixture
def demo_credentials():
    password = os.environ.get("SAUCE_DEMO_PASSWORD")
    if not password:
        raise ConfigurationError("required runtime variable SAUCE_DEMO_PASSWORD is missing")
    return DemoCredentials(SecretValue(password))


@pytest.fixture
def driver(settings):
    browser = DriverFactory.create(settings.browser, settings.headless)
    try:
        yield browser
    finally:
        browser.quit()
