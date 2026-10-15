from __future__ import annotations

from qa_framework.api.schema_validator import validate_schema


class ApiExpect:
    def __init__(self, response) -> None:
        self.response = response

    def status(self, expected: int) -> ApiExpect:
        assert self.response.status_code == expected, (
            f"expected HTTP {expected}, got {self.response.status_code}"
        )
        return self

    def content_type(self, expected: str) -> ApiExpect:
        actual = self.response.headers.get("Content-Type", "")
        assert expected.lower() in actual.lower(), (
            f"expected content type {expected!r}, got {actual!r}"
        )
        return self

    def schema(self, schema: dict) -> ApiExpect:
        validate_schema(self.response.json(), schema)
        return self

    def duration_below(self, seconds: float) -> ApiExpect:
        elapsed = self.response.elapsed.total_seconds()
        assert elapsed < seconds, f"expected duration below {seconds}s, got {elapsed:.3f}s"
        return self
