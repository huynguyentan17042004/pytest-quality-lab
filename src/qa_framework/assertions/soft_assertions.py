from __future__ import annotations


class SoftAssertions:
    def __init__(self) -> None:
        self._errors: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        if not condition:
            self._errors.append(message)

    def assert_all(self) -> None:
        errors, self._errors = self._errors, []
        if errors:
            raise AssertionError("soft assertion failures:\n- " + "\n- ".join(errors))

    @property
    def errors(self) -> tuple[str, ...]:
        return tuple(self._errors)
