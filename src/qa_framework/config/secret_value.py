from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class SecretValue:
    _value: str

    def __post_init__(self) -> None:
        if not isinstance(self._value, str):
            raise TypeError("SecretValue requires a string")

    def reveal(self) -> str:
        return self._value

    def __repr__(self) -> str:
        return "SecretValue('********')"

    def __str__(self) -> str:
        return "********"
