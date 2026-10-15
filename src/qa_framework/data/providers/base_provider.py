from __future__ import annotations

from pathlib import Path
from typing import Protocol


class DataProvider(Protocol):
    def load(self, path: Path, **kwargs) -> list[dict]: ...
