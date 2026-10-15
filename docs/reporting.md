# Reporting

Every run creates `artifacts/runs/<run-id>/manifest.json`, `reports/summary.json`, logs, and bounded artifact directories. Use pytest's JUnit XML and pytest-html exporters for those standard formats. Supporting artifact failures never replace the original test failure.

The pytest hook records redacted exception type, message, and Python traceback while
preserving the primary failure if screenshot or page-source capture also fails.

Multi-run analytics are stored in `artifacts/analytics/quality.db`; see
`quality-analytics.md`. Optional Allure 3 raw results and history setup are documented in
`allure.md`.
