# Postman collections

Collections remain executable Postman suites and are not converted into DataLoader records. The local collection is only for an opt-in localhost runner check. The runner uses an argument list, `shell=False`, local reports, a timeout, and `--no-report-events`.

Runtime variables are merged into a temporary local Postman environment file and passed with `-e`. The temporary file is removed after the subprocess exits, including timeout/failure paths. The runner does not use `postman login`, collection IDs, or `--env-var` for local runs.
