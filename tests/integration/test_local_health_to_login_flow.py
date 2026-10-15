from pathlib import Path

import pytest

from qa_framework.api import BaseApiClient
from tests.support.pages.local_login_page import LocalLoginPage

pytestmark = [pytest.mark.demo, pytest.mark.integration, pytest.mark.api, pytest.mark.ui]


def test_health_check_then_local_login(local_api_server, api_session, driver, settings):
    api = BaseApiClient(local_api_server, session=api_session, timeout=settings.timeout)
    health = api.get("/health")
    assert health.status_code == 200
    assert health.json() == {"status": "ok"}

    fixture = Path(__file__).parents[1] / "framework" / "resources" / "mini_login.html"
    page = LocalLoginPage(driver, fixture.resolve().as_uri(), settings.timeout)
    page.open()
    assert page.login("local_user", "local_password") == "Welcome"


test_health_check_then_local_login.case_id = "DEMO-LOCAL-FLOW-001"
