from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

import pytest

from qa_framework.analytics import AnalyticsStore, generate_dashboard
from qa_framework.config.environment_loader import load_settings
from qa_framework.logging.config import configure_logging
from qa_framework.logging.redaction import environment_secrets
from qa_framework.pytest_plugin.fixtures import *  # noqa: F403
from qa_framework.pytest_plugin.hooks import *  # noqa: F403
from qa_framework.pytest_plugin.markers import MARKERS
from qa_framework.pytest_plugin.options import add_options
from qa_framework.reporting import ArtifactManager, RunContext
from qa_framework.reporting.report_manager import ReportManager
from qa_framework.reporting.result_collector import ResultCollector


def pytest_addoption(parser) -> None:
    add_options(parser)


def pytest_configure(config) -> None:
    for name, description in MARKERS.items():
        config.addinivalue_line("markers", f"{name}: {description}")
    root = Path(str(config.rootpath))
    overrides = {"browser": config.getoption("--browser"), "timeout": config.getoption("--timeout")}
    if config.getoption("--headed"):
        overrides["headless"] = False
    config._qa_settings = load_settings(root, config.getoption("--env"), overrides)
    config._qa_collector = ResultCollector()
    config._qa_redaction_secrets = environment_secrets(os.environ)


def pytest_sessionstart(session) -> None:
    config = session.config
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S.%fZ")
    run_dir = config._qa_settings.project_root / "artifacts" / "runs" / stamp
    config._qa_run_context = RunContext(stamp, run_dir, config._qa_settings.environment)
    config._qa_artifacts = ArtifactManager(
        run_dir, int(config._qa_settings.report.get("max_artifact_bytes", 1_048_576))
    )
    configure_logging(run_dir / "logs", config._qa_redaction_secrets)


def pytest_collection_modifyitems(config, items) -> None:
    external = [item for item in items if item.get_closest_marker("external")]
    if not config.getoption("--run-external"):
        skip = pytest.mark.skip(reason="external test disabled; pass --run-external to opt in")
        for item in external:
            item.add_marker(skip)
        return
    approved = {"DEMO-API-001", "DEMO-UI-001"}
    selected = []
    for item in external:
        case_id = getattr(item.obj, "case_id", None)
        if case_id not in approved:
            raise pytest.UsageError(f"external case is not approved: {item.nodeid}")
        selected.append(case_id)
    if len(selected) > 2:
        raise pytest.UsageError("MVP external budget exceeded: at most 2 external cases per run")
    if selected:
        config.issue_config_time_warning(
            pytest.PytestWarning(f"external plan: {len(selected)} approved case(s), one worker"),
            stacklevel=2,
        )


def pytest_sessionfinish(session, exitstatus) -> None:
    config = session.config
    if hasattr(config, "_qa_run_context"):
        ReportManager(config._qa_run_context.artifact_root).finalize(
            config._qa_run_context, config._qa_collector
        )
        if not config.getoption("--no-analytics") and not config.getoption("collectonly"):
            database = config.getoption("--analytics-db")
            database = (
                Path(database) if database else config.rootpath / "artifacts/analytics/quality.db"
            )
            store = AnalyticsStore(database)
            store.record_run(config._qa_run_context, config._qa_collector, int(exitstatus))
            generate_dashboard(
                database,
                config.rootpath / "artifacts/analytics/dashboard.html",
                config.rootpath / "configs/requirements.yaml",
            )
