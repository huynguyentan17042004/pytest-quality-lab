from __future__ import annotations

from pathlib import Path

from qa_framework.exceptions import PostmanRunnerError


def build_command(
    executable: str,
    collection: str | Path,
    output_dir: Path,
    environment: str | Path | None = None,
) -> list[str]:
    collection_path = Path(collection)
    if not collection_path.is_file():
        raise PostmanRunnerError(f"Postman collection not found: {collection_path}")
    command = [executable, "collection", "run", str(collection_path), "--no-report-events"]
    if environment:
        env_path = Path(environment)
        if not env_path.is_file():
            raise PostmanRunnerError(f"Postman environment not found: {env_path}")
        command.extend(["-e", str(env_path)])
    command.extend(
        [
            "-r",
            "cli,json,junit",
            "--reporter-json-export",
            str(output_dir / "report.json"),
            "--reporter-junit-export",
            str(output_dir / "junit.xml"),
        ]
    )
    return command
