from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from qa_framework.exceptions import PostmanRunnerError
from qa_framework.logging.redaction import redact
from qa_framework.postman.command_builder import build_command
from qa_framework.postman.result import PostmanRunResult, PostmanStatus


class PostmanRunner:
    def __init__(
        self, executable: str = "postman", timeout: float = 60, secrets: tuple[str, ...] = ()
    ) -> None:
        self.executable = executable
        self.timeout = timeout
        self.secrets = secrets
        self.invocations = 0

    def run(self, collection, output_dir, environment=None, variables=None) -> PostmanRunResult:
        if not shutil.which(self.executable):
            raise PostmanRunnerError(f"Postman CLI executable not found: {self.executable}")
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)
        started = time.monotonic()
        self.invocations += 1
        with tempfile.TemporaryDirectory(prefix="qa-postman-") as temp_directory:
            effective_environment = self._runtime_environment(
                environment, variables or {}, Path(temp_directory)
            )
            command = build_command(
                self.executable,
                collection,
                output,
                effective_environment,
            )
            try:
                completed = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    check=False,
                    shell=False,
                )
            except subprocess.TimeoutExpired as exc:
                duration = time.monotonic() - started
                return PostmanRunResult(
                    None,
                    "",
                    redact(exc.stderr or "", self.secrets),
                    (),
                    duration,
                    PostmanStatus.TIMED_OUT,
                )
        duration = time.monotonic() - started
        reports = tuple(
            path for path in (output / "report.json", output / "junit.xml") if path.exists()
        )
        return PostmanRunResult(
            completed.returncode,
            redact(completed.stdout[-4000:], self.secrets),
            redact(completed.stderr[-4000:], self.secrets),
            reports,
            duration,
            PostmanStatus.PASSED if completed.returncode == 0 else PostmanStatus.FAILED,
        )

    @staticmethod
    def _runtime_environment(environment, variables: dict[str, str], temp_dir: Path):
        if not variables:
            return environment
        values: dict[str, dict] = {}
        if environment:
            path = Path(environment)
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                raise PostmanRunnerError(f"cannot read Postman environment: {path}") from exc
            for item in payload.get("values", []):
                if isinstance(item, dict) and item.get("key"):
                    values[str(item["key"])] = dict(item)
        for key, value in variables.items():
            values[key] = {"key": key, "value": value, "enabled": True}
        runtime_path = temp_dir / "runtime.postman_environment.json"
        runtime_path.write_text(
            json.dumps({"name": "qa-framework-runtime", "values": list(values.values())}),
            encoding="utf-8",
        )
        return runtime_path
