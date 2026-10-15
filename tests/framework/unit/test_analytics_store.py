from pathlib import Path

import pytest

from qa_framework.analytics import AnalyticsStore, generate_dashboard
from qa_framework.reporting.models import RunContext, TestResult
from qa_framework.reporting.result_collector import ResultCollector

pytestmark = [pytest.mark.framework, pytest.mark.unit]


def collector(outcome: str) -> ResultCollector:
    result = ResultCollector()
    result.add(
        TestResult(
            "tests/test_example.py::test_case",
            outcome,
            "call",
            0.25,
            "AssertionError: mismatch" if outcome == "failed" else None,
            "CASE-1",
            "REQ-1",
            "AssertionError" if outcome == "failed" else None,
            "Traceback\nAssertionError: mismatch" if outcome == "failed" else None,
        )
    )
    return result


def test_sqlite_history_flaky_rate_and_dashboard(tmp_path: Path):
    database = tmp_path / "quality.db"
    store = AnalyticsStore(database)
    store.record_run(RunContext("run-1", tmp_path / "run-1", "local"), collector("failed"), 1)
    store.record_run(RunContext("run-2", tmp_path / "run-2", "local"), collector("passed"), 0)

    data = store.dashboard_data()
    assert len(data["runs"]) == 2
    assert data["flaky"][0]["nodeid"].endswith("test_case")
    assert data["failures"][0]["failure_fingerprint"]

    requirements = tmp_path / "requirements.yaml"
    requirements.write_text("requirements:\n  - id: REQ-1\n", encoding="utf-8")
    dashboard = generate_dashboard(database, tmp_path / "dashboard.html", requirements)
    text = dashboard.read_text(encoding="utf-8")
    assert "Quality Analytics Dashboard" in text
    assert "100.0%" in text
