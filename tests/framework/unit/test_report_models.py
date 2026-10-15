import pytest

from qa_framework.reporting.models import TestResult
from qa_framework.reporting.result_collector import ResultCollector

pytestmark = [pytest.mark.framework, pytest.mark.unit]


def test_primary_failure_wins_over_teardown_result():
    collector = ResultCollector()
    collector.add(TestResult("test_x", "passed", "setup", 0.1))
    collector.add(TestResult("test_x", "failed", "call", 0.1, "primary"))
    collector.add(TestResult("test_x", "failed", "teardown", 0.1, "cleanup"))
    assert collector.summary() == {"total": 1, "passed": 0, "failed": 1, "skipped": 0}


def test_setup_skip_wins_over_passing_teardown():
    collector = ResultCollector()
    collector.add(TestResult("test_x", "skipped", "setup", 0.1))
    collector.add(TestResult("test_x", "passed", "teardown", 0.1))
    assert collector.summary() == {"total": 1, "passed": 0, "failed": 0, "skipped": 1}
