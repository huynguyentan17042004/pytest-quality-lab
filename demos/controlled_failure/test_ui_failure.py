"""Intentional failure used to demonstrate diagnostic artifact capture."""

import logging
from pathlib import Path

import pytest
from selenium.webdriver.common.by import By

from qa_framework.web import BasePage

pytestmark = [pytest.mark.framework, pytest.mark.integration, pytest.mark.ui]


def test_intentional_ui_failure_creates_diagnostics(driver):
    fixture = Path(__file__).parents[2] / "tests" / "framework" / "resources" / "mini_login.html"
    page = BasePage(driver, fixture.resolve().as_uri(), timeout=2)
    logging.getLogger("qa_framework.ui").info("CONTROLLED_FAILURE: opening local fixture")
    page.open_path()
    page.type((By.ID, "username"), "local_user")
    logging.getLogger("qa_framework.ui").error(
        "CONTROLLED_FAILURE: triggering expected demo assertion failure"
    )
    assert page.text_of((By.ID, "username")) == "intentionally-wrong-value"
