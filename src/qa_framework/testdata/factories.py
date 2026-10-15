from __future__ import annotations

from uuid import uuid4


def unique_name(prefix: str = "test") -> str:
    return f"{prefix}-{uuid4().hex[:12]}"
