# Test strategy

Unit tests use fakes/mocks; integration tests use localhost and controlled HTML. Live demos are `DEMO-API-001` (contract test) and `DEMO-UI-001` (negative locked-account partition). Stable case IDs provide traceability independently of pytest node IDs.

Additional deterministic demos cover a local posts contract and expected 404, CSV-driven positive/negative login partitions, and a health-check-to-login cross-layer flow. `demos/controlled_failure` is excluded from normal collection and intentionally fails to demonstrate diagnostics.
