from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from typing import Any

import requests


class WireMockService:
    """Own a project-scoped WireMock container and its Admin API lifecycle."""

    def __init__(self, project_root: Path, base_url: str) -> None:
        self.project_root = project_root
        self.base_url = base_url.rstrip("/")
        self.compose_file = project_root / "docker-compose.wiremock.yml"
        self.compose_project = "pytest-quality-lab-wiremock"
        self.artifact_dir = project_root / "artifacts" / "wiremock"

    @property
    def _compose_command(self) -> list[str]:
        return [
            "docker",
            "compose",
            "--project-name",
            self.compose_project,
            "--file",
            str(self.compose_file),
        ]

    def start(self, timeout: float = 30.0) -> None:
        self._run_compose("up", "--detach", "--force-recreate")
        deadline = time.monotonic() + timeout
        last_error: Exception | None = None
        while time.monotonic() < deadline:
            try:
                response = requests.get(f"{self.base_url}/__admin/mappings", timeout=1)
                if response.status_code == 200:
                    return
            except requests.RequestException as exc:
                last_error = exc
            time.sleep(0.25)
        logs = self.capture_logs()
        raise RuntimeError(
            f"WireMock did not become ready within {timeout:.0f}s; "
            f"last_error={last_error!r}; logs={logs}"
        )

    def stop(self) -> None:
        self.capture_logs()
        self._run_compose("down", "--remove-orphans", check=False)

    def reset(self) -> None:
        response = requests.post(f"{self.base_url}/__admin/reset", timeout=5)
        response.raise_for_status()
        self.reset_requests()

    def reset_requests(self) -> None:
        response = requests.delete(f"{self.base_url}/__admin/requests", timeout=5)
        response.raise_for_status()

    def add_stub(self, mapping: dict[str, Any]) -> None:
        response = requests.post(f"{self.base_url}/__admin/mappings", json=mapping, timeout=5)
        response.raise_for_status()

    def request_count(self, pattern: dict[str, Any]) -> int:
        response = requests.post(f"{self.base_url}/__admin/requests/count", json=pattern, timeout=5)
        response.raise_for_status()
        return int(response.json()["count"])

    def unmatched_requests(self) -> list[dict[str, Any]]:
        response = requests.get(
            f"{self.base_url}/__admin/requests", params={"unmatched": "true"}, timeout=5
        )
        response.raise_for_status()
        return list(response.json()["requests"])

    def capture_logs(self) -> Path:
        self.artifact_dir.mkdir(parents=True, exist_ok=True)
        target = self.artifact_dir / "container.log"
        result = self._run_compose("logs", "--no-color", check=False)
        target.write_text(result.stdout, encoding="utf-8")
        return target

    def _run_compose(self, *arguments: str, check: bool = True) -> subprocess.CompletedProcess[str]:
        try:
            return subprocess.run(
                [*self._compose_command, *arguments],
                cwd=self.project_root,
                check=check,
                capture_output=True,
                text=True,
                timeout=180,
            )
        except FileNotFoundError as exc:
            raise RuntimeError("Docker CLI is required for --env=wiremock") from exc
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError("Docker Compose command exceeded the 180s safety timeout") from exc
        except subprocess.CalledProcessError as exc:
            details = json.dumps(
                {"stdout": exc.stdout.strip(), "stderr": exc.stderr.strip()},
                ensure_ascii=False,
            )
            raise RuntimeError(f"Docker Compose command failed: {details}") from exc
