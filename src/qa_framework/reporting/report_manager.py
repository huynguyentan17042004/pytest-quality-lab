from __future__ import annotations

import json
from pathlib import Path

from qa_framework.reporting.manifest import write_manifest


class ReportManager:
    def __init__(self, run_dir: Path) -> None:
        self.run_dir = Path(run_dir)

    def finalize(self, context, collector) -> None:
        reports = self.run_dir / "reports"
        reports.mkdir(parents=True, exist_ok=True)
        summary = collector.summary()
        (reports / "summary.json").write_text(
            json.dumps(
                {"counts": summary, "results": [item.as_dict() for item in collector.results]},
                indent=2,
            ),
            encoding="utf-8",
        )
        write_manifest(self.run_dir / "manifest.json", context, summary, ["reports/summary.json"])
