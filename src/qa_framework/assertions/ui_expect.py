def contains_text(actual: str, expected: str) -> None:
    assert expected in actual, f"expected {expected!r} in {actual!r}"
