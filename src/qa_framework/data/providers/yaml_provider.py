from pathlib import Path

import yaml

from qa_framework.exceptions import DataValidationError


class YamlDataProvider:
    def load(self, path: Path, **_kwargs) -> list[dict]:
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            raise DataValidationError(f"{path}: invalid YAML") from exc
        if not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
            raise DataValidationError(f"{path}: YAML root must be a list of objects")
        return data
