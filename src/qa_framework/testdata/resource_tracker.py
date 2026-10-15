from __future__ import annotations

import logging
from collections.abc import Callable

logger = logging.getLogger("qa_framework.testdata")


class ResourceTracker:
    def __init__(self) -> None:
        self._cleanups: list[tuple[Callable, tuple, dict]] = []
        self._cleaned = False

    def register(self, cleanup: Callable, *args, **kwargs) -> None:
        if self._cleaned:
            raise RuntimeError("cannot register cleanup after tracker was cleaned")
        self._cleanups.append((cleanup, args, kwargs))

    def cleanup(self) -> list[Exception]:
        if self._cleaned:
            return []
        self._cleaned = True
        errors = []
        while self._cleanups:
            cleanup, args, kwargs = self._cleanups.pop()
            try:
                cleanup(*args, **kwargs)
            except Exception as exc:  # cleanup must continue best effort
                errors.append(exc)
                logger.warning("resource cleanup failed: %s", exc)
        return errors
