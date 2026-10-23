import pytest

from tests.support.api_server import run_demo_api
from tests.support.wiremock_service import WireMockService

pytest_plugins = ["qa_framework.pytest_plugin.plugin", "pytester"]


@pytest.fixture
def local_api_server():
    with run_demo_api() as base_url:
        yield base_url


@pytest.fixture(scope="session")
def wiremock_service(request):
    settings = request.config._qa_settings
    if settings.environment != "wiremock":
        pytest.skip("requires --env=wiremock")
    service = WireMockService(settings.project_root, settings.api_base_url)
    try:
        service.start()
        yield service
    finally:
        service.stop()


@pytest.fixture
def isolated_wiremock(wiremock_service):
    wiremock_service.reset()
    yield wiremock_service
    wiremock_service.reset()
