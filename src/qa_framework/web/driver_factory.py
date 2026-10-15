from __future__ import annotations

from typing import Any

from selenium import webdriver

from qa_framework.exceptions import ConfigurationError
from qa_framework.web.browser_options import chrome_options, firefox_options


class DriverFactory:
    sessions_created = 0

    @classmethod
    def create(cls, browser: str = "chrome", headless: bool = True, download_dir=None):
        driver: Any
        if browser == "chrome":
            driver = webdriver.Chrome(options=chrome_options(headless, download_dir))
        elif browser == "firefox":
            driver = webdriver.Firefox(options=firefox_options(headless))
        else:
            raise ConfigurationError(f"unsupported browser: {browser}")
        cls.sessions_created += 1
        driver.implicitly_wait(0)
        return driver
