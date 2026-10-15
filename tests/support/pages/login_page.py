from selenium.webdriver.common.by import By

from qa_framework.web import BasePage


class LoginPage(BasePage):
    USERNAME = (By.ID, "user-name")
    PASSWORD = (By.ID, "password")
    SUBMIT = (By.ID, "login-button")
    ERROR = (By.CSS_SELECTOR, "[data-test='error']")

    def open(self) -> None:
        self.open_path("")
        self.visible(self.USERNAME)

    def login(self, username: str, password: str) -> None:
        self.type(self.USERNAME, username)
        self.type(self.PASSWORD, password)
        self.click(self.SUBMIT)

    def error_message(self) -> str:
        return self.text_of(self.ERROR)
