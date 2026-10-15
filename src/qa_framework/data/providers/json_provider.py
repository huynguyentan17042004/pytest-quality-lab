import json
from pathlib import Path

from qa_framework.exceptions import DataValidationError


class JsonDataProvider:
    def load(self, path: Path, **_kwargs) -> list[dict]:
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            raise DataValidationError(f"{path}: invalid JSON at line {exc.lineno}") from exc
        if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
            raise DataValidationError(f"{path}: JSON root must be a list of objects")
        return data
