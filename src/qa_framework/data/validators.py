from __future__ import annotations

import re
from pathlib import Path

from qa_framework.exceptions import DataValidationError

PLACEHOLDER = re.compile(r"^\$\{[A-Z][A-Z0-9_]*\}$")


def validate_rows(rows: list[dict], path: Path) -> None:
    if not rows:
        raise DataValidationError(f"{path}: data file is empty")
    case_ids: set[str] = set()
    for number, row in enumerate(rows, start=2):
        case_id = row.get("case_id")
        if not case_id:
            raise DataValidationError(f"{path}: row {number}, field case_id is required")
        if case_id in case_ids:
            raise DataValidationError(f"{path}: row {number}, duplicate case_id {case_id!r}")
        case_ids.add(str(case_id))
        for field, value in row.items():
            if (
                isinstance(value, str)
                and value.startswith("${")
                and not PLACEHOLDER.fullmatch(value)
            ):
                raise DataValidationError(
                    f"{path}: row {number}, field {field} has invalid placeholder"
                )
