# CI/CD

The repository workflow is `.github/workflows/quality.yml`. It runs deterministic
quality checks and local browser tests on pushes and pull requests. The two approved
external demos run only through a manual dispatch with `run_external=true` and the
`SAUCE_DEMO_PASSWORD` repository secret configured.

## Pull request and main branch

Two zero-public-traffic jobs run independently:

1. `quality-and-local`: Ruff, mypy, unit tests, localhost API tests, reporting tests, and local API demos.
2. `local-browser`: controlled HTML UI tests, data-driven positive/negative login demos, and a localhost API-to-UI flow with headless Chrome.

Both jobs have a 15-minute wall-clock timeout and publish local artifacts even after a test failure.

## External demonstrations

`approved-external-demos` exists only for `workflow_dispatch` with `run_external=true`. It runs exactly `DEMO-API-001` and `DEMO-UI-001`, one worker, `--maxfail=1`, and obtains the public SauceDemo password from the `SAUCE_DEMO_PASSWORD` repository secret.

There is no scheduled external traffic and no automatic rerun.

## Postman

The Postman CLI process contract is mandatory and covered by mocked unit tests. The localhost collection integration test runs automatically when a `postman` executable is available and otherwise reports a visible skip. Installing or authenticating Postman is intentionally outside automatic CI and local setup.
