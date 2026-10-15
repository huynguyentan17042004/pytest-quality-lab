from __future__ import annotations

from collections import Counter

from qa_framework.reporting.models import TestResult


class ResultCollector:
    def __init__(self) -> None:
        self.results: list[TestResult] = []

    def add(self, result: TestResult) -> None:
        self.results.append(result)

    def summary(self) -> dict:
        counts = Counter(result.outcome for result in self.final_results())
        return {
            "total": sum(counts.values()),
            "passed": counts["passed"],
            "failed": counts["failed"],
            "skipped": counts["skipped"],
        }

    def final_results(self) -> list[TestResult]:
        grouped: dict[str, list[TestResult]] = {}
        for result in self.results:
            grouped.setdefault(result.nodeid, []).append(result)
        final = []
        for nodeid, phases in grouped.items():
            chosen = next((item for item in phases if item.outcome == "failed"), None)
            chosen = chosen or next((item for item in phases if item.outcome == "skipped"), None)
            chosen = chosen or next((item for item in phases if item.phase == "call"), phases[-1])
            final.append(
                TestResult(
                    nodeid=nodeid,
                    outcome=chosen.outcome,
                    phase="final",
                    duration=sum(item.duration for item in phases),
                    longrepr=chosen.longrepr,
                    case_id=chosen.case_id,
                    requirement_id=chosen.requirement_id,
                    failure_type=chosen.failure_type,
                    traceback=chosen.traceback,
                )
            )
        return final
