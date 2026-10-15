from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class ApiResponse:
    status_code: int
    headers: Mapping[str, str]
    elapsed_seconds: float
    body: Any
    raw: Any

    def json(self) -> Any:
        return self.body
