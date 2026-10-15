from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from qa_framework.reporting.models import RunContext


def write_manifest(
    path: Path, context: RunContext, counts: dict, reports: list[str] | None = None
) -> None:
    payload = {
        "schema_version": 1,
        "run": {**asdict(context), "artifact_root": str(context.artifact_root)},
        "counts": counts,
        "reports": reports or [],
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
