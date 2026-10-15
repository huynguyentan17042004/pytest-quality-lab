import pytest

from tests.support.api_server import run_demo_api

pytest_plugins = ["qa_framework.pytest_plugin.plugin", "pytester"]


@pytest.fixture
def local_api_server():
    with run_demo_api() as base_url:
        yield base_url
