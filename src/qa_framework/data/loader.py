from __future__ import annotations

from dataclasses import is_dataclass
from pathlib import Path
from typing import cast

import pytest

from qa_framework.data.provider_factory import DataProviderFactory
from qa_framework.data.validators import validate_rows
from qa_framework.exceptions import DataProviderError, DataValidationError


class DataLoader:
    @staticmethod
    def load(path: str | Path, model=None, **kwargs) -> list:
        source = Path(path)
        if not source.is_file():
            raise DataProviderError(f"data file not found: {source}")
        if source.stat().st_size == 0:
            raise DataValidationError(f"{source}: data file is empty")
        rows = cast(list[dict], DataProviderFactory.create(source).load(source, **kwargs))
        validate_rows(rows, source)
        if model is None:
            return rows
        try:
            return [model(**row) for row in rows]
        except (TypeError, ValueError) as exc:
            kind = "dataclass" if is_dataclass(model) else "model"
            raise DataValidationError(
                f"{source}: cannot convert row to {kind} {model.__name__}: {exc}"
            ) from exc

    @staticmethod
    def pytest_params(path: str | Path, model=None, id_field: str = "case_id", **kwargs) -> list:
        cases = DataLoader.load(path, model=model, **kwargs)
        params = []
        for case in cases:
            case_id = getattr(case, id_field, None) if model else case.get(id_field)
            if not case_id:
                raise DataValidationError(f"{path}: id field {id_field!r} is missing")
            params.append(pytest.param(case, id=str(case_id)))
        return params
