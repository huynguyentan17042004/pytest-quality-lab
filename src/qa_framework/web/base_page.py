from __future__ import annotations

from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


class BasePage:
    def __init__(self, driver, base_url: str, timeout: float = 10.0) -> None:
        self.driver = driver
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def open_path(self, path: str = "") -> None:
        target = self.base_url if not path else f"{self.base_url}/{path.lstrip('/')}"
        self.driver.get(target)

    def visible(self, locator):
        return WebDriverWait(self.driver, self.timeout).until(
            ec.visibility_of_element_located(locator)
        )

    def clickable(self, locator):
        return WebDriverWait(self.driver, self.timeout).until(ec.element_to_be_clickable(locator))

    def click(self, locator) -> None:
        self.clickable(locator).click()

    def type(self, locator, value: str, clear: bool = True) -> None:
        element = self.visible(locator)
        if clear:
            element.clear()
        element.send_keys(value)

    def text_of(self, locator) -> str:
        return str(self.visible(locator).text)

    def wait_for_url(self, fragment: str) -> None:
        WebDriverWait(self.driver, self.timeout).until(ec.url_contains(fragment))

    def wait_for_text(self, locator, text: str) -> None:
        WebDriverWait(self.driver, self.timeout).until(
            ec.text_to_be_present_in_element(locator, text)
        )

    def wait_for_invisibility(self, locator) -> None:
        WebDriverWait(self.driver, self.timeout).until(ec.invisibility_of_element_located(locator))
