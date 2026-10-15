from __future__ import annotations

import hashlib
import re
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from qa_framework.reporting.models import RunContext, TestResult
from qa_framework.reporting.result_collector import ResultCollector

SCHEMA = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS runs (
  run_id TEXT PRIMARY KEY, started_at TEXT NOT NULL, finished_at TEXT NOT NULL,
  environment TEXT NOT NULL, exit_status INTEGER NOT NULL,
  total INTEGER NOT NULL, passed INTEGER NOT NULL, failed INTEGER NOT NULL,
  skipped INTEGER NOT NULL, duration REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS test_results (
  id INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL REFERENCES runs(run_id),
  nodeid TEXT NOT NULL, case_id TEXT, requirement_id TEXT, outcome TEXT NOT NULL,
  duration REAL NOT NULL, failure_type TEXT, failure_message TEXT,
  traceback TEXT, failure_fingerprint TEXT,
  UNIQUE(run_id, nodeid)
);
CREATE INDEX IF NOT EXISTS idx_results_nodeid ON test_results(nodeid);
CREATE INDEX IF NOT EXISTS idx_results_requirement ON test_results(requirement_id);
CREATE INDEX IF NOT EXISTS idx_results_failure ON test_results(failure_fingerprint);
"""


def failure_fingerprint(result: TestResult) -> str | None:
    if result.outcome != "failed":
        return None
    message = re.sub(r"0x[0-9a-fA-F]+|\d+(?:\.\d+)?s", "<variable>", result.longrepr or "")
    raw = f"{result.failure_type or 'Failure'}|{message[-1000:]}"
    return hashlib.sha256(raw.encode("utf-8", errors="replace")).hexdigest()[:16]


class AnalyticsStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as connection:
            connection.executescript(SCHEMA)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA busy_timeout=5000")
        return connection

    def record_run(self, context: RunContext, collector: ResultCollector, exit_status: int) -> None:
        results = collector.final_results()
        counts = collector.summary()
        duration = sum(result.duration for result in results)
        finished_at = datetime.now(timezone.utc).isoformat()
        with self.connect() as connection:
            connection.execute(
                "INSERT OR REPLACE INTO runs VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    context.run_id,
                    context.started_at,
                    finished_at,
                    context.environment,
                    exit_status,
                    counts["total"],
                    counts["passed"],
                    counts["failed"],
                    counts["skipped"],
                    duration,
                ),
            )
            connection.executemany(
                """INSERT OR REPLACE INTO test_results
                (run_id,nodeid,case_id,requirement_id,outcome,duration,failure_type,
                 failure_message,traceback,failure_fingerprint)
                VALUES (?,?,?,?,?,?,?,?,?,?)""",
                [
                    (
                        context.run_id,
                        result.nodeid,
                        result.case_id,
                        result.requirement_id,
                        result.outcome,
                        result.duration,
                        result.failure_type,
                        (result.longrepr or "")[-4000:] or None,
                        (result.traceback or "")[-12000:] or None,
                        failure_fingerprint(result),
                    )
                    for result in results
                ],
            )

    def dashboard_data(self, limit: int = 20) -> dict:
        with self.connect() as connection:
            runs = [
                dict(row)
                for row in connection.execute(
                    "SELECT * FROM runs ORDER BY started_at DESC LIMIT ?", (limit,)
                )
            ]
            failures = [
                dict(row)
                for row in connection.execute(
                    """SELECT r.started_at,t.nodeid,t.case_id,t.requirement_id,t.failure_type,
                t.failure_message,t.failure_fingerprint FROM test_results t
                JOIN runs r USING(run_id) WHERE t.outcome='failed'
                ORDER BY r.started_at DESC LIMIT 30"""
                )
            ]
            stability = [
                dict(row)
                for row in connection.execute(
                    """SELECT nodeid, COUNT(*) executions,
                SUM(outcome='passed') passes, SUM(outcome='failed') failures,
                AVG(duration) avg_duration FROM test_results GROUP BY nodeid"""
                )
            ]
            covered = connection.execute(
                """SELECT COUNT(DISTINCT requirement_id) FROM test_results
                WHERE requirement_id IS NOT NULL"""
            ).fetchone()[0]
        flaky = [row for row in stability if row["passes"] and row["failures"]]
        return {
            "runs": runs,
            "failures": failures,
            "stability": stability,
            "flaky": flaky,
            "covered_requirements": covered,
        }
