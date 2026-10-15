class text_contains_casefold:
    def __init__(self, locator, expected: str) -> None:
        self.locator = locator
        self.expected = expected.casefold()

    def __call__(self, driver):
        element = driver.find_element(*self.locator)
        return element if self.expected in element.text.casefold() else False
