import pytest

from tests.support.pages.login_page import LoginPage

pytestmark = [
    pytest.mark.demo,
    pytest.mark.ui,
    pytest.mark.negative,
    pytest.mark.external,
    pytest.mark.serial,
]


@pytest.fixture
def login_page(driver, settings):
    assert settings.ui_base_url == "https://www.saucedemo.com", (
        "external UI host is not allowlisted"
    )
    return LoginPage(driver, settings.ui_base_url, settings.timeout)


def test_locked_out_user_sees_error(login_page, demo_credentials):
    login_page.open()
    login_page.login("locked_out_user", demo_credentials.password.reveal())
    assert "locked out" in login_page.error_message().lower()
    assert "inventory" not in login_page.driver.current_url


test_locked_out_user_sees_error.case_id = "DEMO-UI-001"
