from __future__ import annotations

import logging
import traceback as traceback_module

import pytest

from qa_framework.logging.context import bind_context, clear_context
from qa_framework.logging.redaction import redact
from qa_framework.reporting.models import TestResult

logger = logging.getLogger("qa_framework.reporting")


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()
    collector = item.config._qa_collector
    requirement = item.get_closest_marker("requirement")
    requirement_id = str(requirement.args[0]) if requirement and requirement.args else None
    case_id = getattr(item.obj, "case_id", None)
    if hasattr(item, "callspec"):
        for value in item.callspec.params.values():
            case_id = getattr(value, "case_id", case_id)
            requirement_id = getattr(value, "requirement_id", requirement_id)
    failure_type = call.excinfo.type.__name__ if call.excinfo else None
    trace = None
    secrets = getattr(item.config, "_qa_redaction_secrets", ())
    if call.excinfo:
        trace = redact(
            "".join(
                traceback_module.format_exception(
                    call.excinfo.type, call.excinfo.value, call.excinfo.tb
                )
            ),
            secrets,
        )
        logger.error(
            "Test phase failed: nodeid=%s phase=%s type=%s\n%s",
            item.nodeid,
            report.when,
            failure_type,
            trace,
        )
    collector.add(
        TestResult(
            item.nodeid,
            report.outcome,
            report.when,
            report.duration,
            str(redact(str(report.longrepr), secrets)) if report.failed else None,
            str(case_id) if case_id else None,
            requirement_id,
            failure_type,
            str(trace) if trace else None,
        )
    )
    if report.failed:
        driver = item.funcargs.get("driver")
        if driver is not None:
            try:
                item.config._qa_artifacts.capture_webdriver_failure(item.nodeid, driver)
            except Exception as exc:
                logger.warning(
                    "failure artifact capture failed without replacing primary failure: %s", exc
                )


def pytest_runtest_setup(item) -> None:
    bind_context(
        run_id=item.config._qa_run_context.run_id,
        test_node_id=item.nodeid,
        environment=item.config._qa_settings.environment,
    )


def pytest_runtest_teardown(item) -> None:
    clear_context()
