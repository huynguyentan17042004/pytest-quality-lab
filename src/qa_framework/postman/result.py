from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class PostmanStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"
    TIMED_OUT = "timed_out"


@dataclass(frozen=True, slots=True)
class PostmanRunResult:
    exit_code: int | None
    stdout_summary: str
    stderr_summary: str
    report_paths: tuple[Path, ...]
    duration: float
    status: PostmanStatus
