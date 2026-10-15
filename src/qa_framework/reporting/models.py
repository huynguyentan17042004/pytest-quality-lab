from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True, slots=True)
class RunContext:
    run_id: str
    artifact_root: Path
    environment: str
    started_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass(frozen=True, slots=True)
class TestResult:
    __test__ = False

    nodeid: str
    outcome: str
    phase: str
    duration: float
    longrepr: str | None = None
    case_id: str | None = None
    requirement_id: str | None = None
    failure_type: str | None = None
    traceback: str | None = None

    def as_dict(self) -> dict:
        return asdict(self)
