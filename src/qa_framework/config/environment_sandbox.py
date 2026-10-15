from __future__ import annotations

import os
from collections.abc import Mapping


class EnvironmentSandbox:
    """Process-local environment isolation for one test or context."""

    def __init__(self, initial: Mapping[str, str] | None = None) -> None:
        self.initial = dict(initial or {})
        self._snapshot: dict[str, str] | None = None

    def __enter__(self) -> EnvironmentSandbox:
        self._snapshot = dict(os.environ)
        os.environ.update(self.initial)
        return self

    def set(self, name: str, value: str) -> None:
        os.environ[name] = value

    def unset(self, name: str) -> None:
        os.environ.pop(name, None)

    def __exit__(self, *_exc: object) -> None:
        if self._snapshot is None:
            return
        os.environ.clear()
        os.environ.update(self._snapshot)
        self._snapshot = None
