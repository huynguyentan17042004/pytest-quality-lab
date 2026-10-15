# Demonstrations

Normal local demos live under `tests/api`, `tests/ui`, and `tests/integration` and must pass.

The controlled-failure demo is excluded from normal collection. Run it explicitly when demonstrating logging, screenshot, page-source capture, failure reporting, and preservation of the original assertion:

```bash
python -m pytest demos/controlled_failure/test_ui_failure.py -q
```

Exit code `1` is expected. Inspect the newest directory under `artifacts/runs/`; it must contain `logs/run.log`, `logs/run.jsonl`, a PNG in `screenshots/`, an HTML page source, `reports/summary.json`, and `manifest.json` with one failed test.
