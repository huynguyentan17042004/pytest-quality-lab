from pathlib import Path

import pytest

from qa_framework.data import DataLoader
from tests.support.models import LoginCase
from tests.support.pages.local_login_page import LocalLoginPage

pytestmark = [pytest.mark.demo, pytest.mark.ui, pytest.mark.integration]

CASES = Path(__file__).parents[1] / "data" / "ui" / "local_login_cases.csv"


@pytest.fixture
def local_login_page(driver, settings):
    fixture = Path(__file__).parents[1] / "framework" / "resources" / "mini_login.html"
    return LocalLoginPage(driver, fixture.resolve().as_uri(), settings.timeout)


@pytest.mark.parametrize(
    "case",
    DataLoader.pytest_params(CASES, model=LoginCase),
)
def test_local_login_partitions(local_login_page, case: LoginCase):
    local_login_page.open()
    actual_message = local_login_page.login(case.username, case.password)
    assert actual_message == case.expected_message, (
        f"{case.case_id} ({case.technique}) expected {case.expected_message!r}, "
        f"got {actual_message!r}"
    )
