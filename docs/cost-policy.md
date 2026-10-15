# Cost and execution policy

Default runs are offline-first. `external` tests are skipped unless `--run-external` is supplied. The allowlist contains only `DEMO-API-001` and `DEMO-UI-001`, with a maximum of two selected cases, one API request, one headless browser, no reruns, and no parallel execution.
