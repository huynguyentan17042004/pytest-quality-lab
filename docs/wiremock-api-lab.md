# WireMock business virtualization lab

This lab exercises the real `BaseApiClient` and `PostsClient` over HTTP while replacing only
the remote posts service. Pytest owns the Docker lifecycle, readiness wait, state reset,
request journal, log capture, and cleanup.

## Business coverage

| Area | Automated behavior |
| --- | --- |
| Read | A known post returns 200 and satisfies the shared JSON Schema. |
| Missing data | An unknown numeric identifier returns a typed 404 error. |
| Service outage | A deterministic 503 is surfaced without an unintended retry. |
| Filtering | Query parameters and correlation headers must match the dependency contract. |
| Create validation | A valid post is created; a blank title receives a controlled 422. |
| Eventual recovery | The first GET returns 503 and the configured retry returns 200. |
| Latency | A delayed dependency becomes `ApiTimeoutError`. |
| Corrupt payload | Invalid JSON remains visible to the consumer. |
| Broken connection | An empty HTTP response becomes `ApiTransportError`. |
| Interaction | The request journal verifies request method, path, metadata, and call count. |

These tests validate client behavior against a controlled dependency. They do not prove that a
production provider implements the same contract, so critical flows still require real integration
checks.

## One-command execution

Docker Desktop or Docker Engine with Compose must be available. The test fixture starts and stops
the project-scoped container automatically:

```bash
python -m pytest tests/api/test_wiremock_posts_api.py \
  --env=wiremock -v \
  --html=artifacts/wiremock-report.html \
  --self-contained-html \
  --junitxml=artifacts/wiremock-junit.xml \
  --alluredir=artifacts/allure-results
```

Container output is retained at `artifacts/wiremock/container.log`, including when a test fails.
Running the normal local suite does not start Docker because only WireMock tests depend on the
managed fixture and skip outside `--env=wiremock`.

## Isolation model

- File-backed mappings provide the deterministic 200, 404, and 503 baseline.
- Dynamic mappings are installed through the Admin API for each advanced case.
- `POST /__admin/reset` restores file mappings and scenario state around every test.
- `DELETE /__admin/requests` clears request history around every test.
- The fixed Compose project name prevents cleanup from targeting unrelated Compose projects.
- The suite remains serial because a shared request journal and scenario store are stateful.

Do not run this test module with multiple pytest workers against the same port. Parallel execution
requires a unique WireMock container and host port for each worker.
