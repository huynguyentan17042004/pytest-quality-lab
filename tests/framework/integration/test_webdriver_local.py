import shutil
from pathlib import Path

import pytest
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By

from qa_framework.web import BasePage, DriverFactory

pytestmark = [pytest.mark.framework, pytest.mark.integration, pytest.mark.ui]


@pytest.fixture
def local_driver():
    if not (
        shutil.which("google-chrome")
        or shutil.which("chromium")
        or Path("/Applications/Google Chrome.app").exists()
    ):
        pytest.skip("local Chrome is not installed")
    try:
        browser = DriverFactory.create("chrome", headless=True)
    except Exception as exc:
        pytest.skip(f"local Chrome/WebDriver unavailable: {type(exc).__name__}")
    try:
        yield browser
    finally:
        browser.quit()


def test_page_actions_and_delayed_explicit_wait(local_driver):
    uri = (Path(__file__).parents[1] / "resources" / "mini_login.html").resolve().as_uri()
    page = BasePage(local_driver, uri, timeout=2)
    page.open_path()
    page.type((By.ID, "username"), "local_user")
    page.type((By.ID, "password"), "local_password")
    page.click((By.ID, "login"))
    page.wait_for_text((By.ID, "message"), "Welcome")
    assert page.text_of((By.ID, "message")) == "Welcome"


def test_wait_timeout_is_observable(local_driver):
    uri = (Path(__file__).parents[1] / "resources" / "mini_login.html").resolve().as_uri()
    page = BasePage(local_driver, uri, timeout=0.1)
    page.open_path()
    with pytest.raises(TimeoutException):
        page.visible((By.ID, "missing"))
