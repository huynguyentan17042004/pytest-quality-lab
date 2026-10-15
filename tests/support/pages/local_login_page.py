import logging

from selenium.webdriver.common.by import By

from qa_framework.web import BasePage

logger = logging.getLogger("qa_framework.ui")


class LocalLoginPage(BasePage):
    USERNAME = (By.ID, "username")
    PASSWORD = (By.ID, "password")
    SUBMIT = (By.ID, "login")
    MESSAGE = (By.ID, "message")

    def open(self) -> None:
        logger.info("Opening controlled local login page")
        self.open_path()
        self.visible(self.USERNAME)

    def login(self, username: str, password: str) -> str:
        logger.info("Submitting controlled local login form")
        self.type(self.USERNAME, username)
        self.type(self.PASSWORD, password)
        self.click(self.SUBMIT)
        expected = "Welcome" if username == "local_user" else "Invalid credentials"
        self.wait_for_text(self.MESSAGE, expected)
        return self.text_of(self.MESSAGE)
