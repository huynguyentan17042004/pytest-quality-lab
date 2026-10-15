from __future__ import annotations

# ruff: noqa: E501
import html
import json
from pathlib import Path

import yaml

from qa_framework.analytics.store import AnalyticsStore


def _requirements_count(path: Path | None) -> int:
    if not path or not path.is_file():
        return 0
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return len(data.get("requirements", []))


def generate_dashboard(
    database: str | Path,
    output: str | Path,
    requirements_path: str | Path | None = None,
) -> Path:
    store = AnalyticsStore(database)
    data = store.dashboard_data()
    runs = data["runs"]
    latest = (
        runs[0] if runs else {"total": 0, "passed": 0, "failed": 0, "skipped": 0, "duration": 0}
    )
    total_requirements = _requirements_count(Path(requirements_path) if requirements_path else None)
    covered = int(data["covered_requirements"])
    coverage = 100 * covered / total_requirements if total_requirements else 0
    stable_tests = len(data["stability"])
    flaky_rate = 100 * len(data["flaky"]) / stable_tests if stable_tests else 0
    decided = latest["passed"] + latest["failed"]
    pass_rate = 100 * latest["passed"] / decided if decided else 0

    run_rows = (
        "".join(
            f"<tr><td>{html.escape(run['started_at'])}</td><td>{run['environment']}</td>"
            f"<td>{run['passed']}</td><td>{run['failed']}</td><td>{run['skipped']}</td>"
            f"<td>{run['total']}</td><td>{run['duration']:.3f}s</td></tr>"
            for run in runs
        )
        or "<tr><td colspan='7'>No runs recorded</td></tr>"
    )
    failure_rows = (
        "".join(
            f"<tr><td>{html.escape(item['started_at'])}</td>"
            f"<td>{html.escape(item['nodeid'])}</td>"
            f"<td>{html.escape(item['failure_type'] or 'Failure')}</td>"
            f"<td><code>{html.escape(item['failure_fingerprint'] or '')}</code></td></tr>"
            for item in data["failures"]
        )
        or "<tr><td colspan='4'>No failures recorded</td></tr>"
    )
    flaky_rows = (
        "".join(
            f"<tr><td>{html.escape(item['nodeid'])}</td><td>{item['passes']}</td>"
            f"<td>{item['failures']}</td><td>{item['avg_duration']:.3f}s</td></tr>"
            for item in data["flaky"]
        )
        or "<tr><td colspan='4'>No historically unstable tests</td></tr>"
    )
    trend = json.dumps(list(reversed(runs)))
    document = f"""<!doctype html><html><head><meta charset='utf-8'>
<title>Quality Analytics Dashboard</title><style>
body{{font:14px system-ui;margin:0;background:#f5f7fb;color:#18212f}}main{{max-width:1200px;margin:auto;padding:28px}}
.cards{{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}}.card,section{{background:white;border-radius:12px;padding:18px;box-shadow:0 2px 12px #15213a12}}
.value{{font-size:30px;font-weight:750}}section{{margin-top:18px}}table{{width:100%;border-collapse:collapse}}th,td{{text-align:left;padding:9px;border-bottom:1px solid #e8edf5}}th{{color:#526174}}.bar{{height:12px;background:#e8edf5;border-radius:9px;overflow:hidden}}.bar i{{display:block;height:100%;background:#2d7ff9}}code{{font-size:12px}}</style></head>
<body><main><h1>Quality Analytics Dashboard</h1><p>SQLite-backed local history · latest {len(runs)} runs</p>
<div class='cards'><div class='card'><div>Pass rate (excluding skipped)</div><div class='value'>{pass_rate:.1f}%</div></div>
<div class='card'><div>Flaky rate</div><div class='value'>{flaky_rate:.1f}%</div></div>
<div class='card'><div>Execution time</div><div class='value'>{latest["duration"]:.2f}s</div></div>
<div class='card'><div>Requirement coverage</div><div class='value'>{coverage:.1f}%</div><div>{covered}/{total_requirements}</div></div></div>
<section><h2>Pass-rate trend</h2><div id='trend'></div></section>
<section><h2>Run history</h2><table><tr><th>Started</th><th>Environment</th><th>Passed</th><th>Failed</th><th>Skipped</th><th>Total</th><th>Duration</th></tr>{run_rows}</table></section>
<section><h2>Flaky candidates</h2><table><tr><th>Test</th><th>Passes</th><th>Failures</th><th>Avg duration</th></tr>{flaky_rows}</table></section>
<section><h2>Failure history</h2><table><tr><th>Started</th><th>Test</th><th>Type</th><th>Fingerprint</th></tr>{failure_rows}</table></section>
<script>const runs={trend};document.querySelector('#trend').innerHTML=runs.map(r=>{{const decided=r.passed+r.failed;const p=decided?100*r.passed/decided:0;return `<p>${{r.started_at}} · ${{p.toFixed(1)}}%</p><div class="bar"><i style="width:${{p}}%"></i></div>`}}).join('')||'No history';</script>
</main></body></html>"""
    destination = Path(output)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(document, encoding="utf-8")
    return destination
