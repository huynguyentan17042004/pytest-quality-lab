from __future__ import annotations

from pathlib import Path

from qa_framework.data.providers import (
    CsvDataProvider,
    ExcelDataProvider,
    JsonDataProvider,
    YamlDataProvider,
)
from qa_framework.exceptions import UnsupportedDataFormatError


class DataProviderFactory:
    _providers = {
        ".csv": CsvDataProvider,
        ".json": JsonDataProvider,
        ".yaml": YamlDataProvider,
        ".yml": YamlDataProvider,
        ".xlsx": ExcelDataProvider,
    }

    @classmethod
    def register(cls, extension: str, provider) -> None:
        cls._providers[
            extension.lower() if extension.startswith(".") else f".{extension.lower()}"
        ] = provider

    @classmethod
    def create(cls, path: str | Path):
        extension = Path(path).suffix.lower()
        try:
            return cls._providers[extension]()
        except KeyError as exc:
            raise UnsupportedDataFormatError(
                f"unsupported data format {extension!r} for {path}"
            ) from exc
