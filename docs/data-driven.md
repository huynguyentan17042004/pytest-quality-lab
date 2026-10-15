# Data-driven testing

`DataLoader` supports CSV, JSON, YAML, and XLSX. It validates unique `case_id` values at collection time but leaves `${VARIABLE}` placeholders unresolved. Runtime resolution creates redacted `SecretValue` objects.

Hypothesis property tests complement these example tables for broad invariant coverage;
see `property-based-testing.md`. Environment overrides should use `isolated_env` or
`EnvironmentSandbox` so generated examples cannot leak process state to later tests.
