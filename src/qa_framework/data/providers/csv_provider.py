import csv
from pathlib import Path

from qa_framework.exceptions import DataValidationError


class CsvDataProvider:
    def load(self, path: Path, **_kwargs) -> list[dict]:
        with path.open(newline="", encoding="utf-8-sig") as stream:
            reader = csv.DictReader(stream)
            if not reader.fieldnames:
                raise DataValidationError(f"{path}: CSV header is required")
            return list(reader)
