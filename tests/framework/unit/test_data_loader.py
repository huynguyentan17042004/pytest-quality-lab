from dataclasses import dataclass

import pytest
from openpyxl import Workbook

from qa_framework.data import DataLoader
from qa_framework.data.converters import resolve_runtime_variables
from qa_framework.exceptions import (
    DataValidationError,
    MissingVariableError,
    UnsupportedDataFormatError,
)

pytestmark = [pytest.mark.framework, pytest.mark.unit]


@dataclass(frozen=True, slots=True)
class Case:
    case_id: str
    value: str


@pytest.mark.parametrize(
    ("suffix", "content"),
    [
        (".csv", "case_id,value\nC-1,yes\n"),
        (".json", '[{"case_id":"C-1","value":"yes"}]'),
        (".yaml", "- case_id: C-1\n  value: 'yes'\n"),
    ],
)
def test_text_providers_share_one_api(tmp_path, suffix, content):
    path = tmp_path / f"cases{suffix}"
    path.write_text(content, encoding="utf-8")
    cases = DataLoader.load(path, model=Case)
    assert cases[0].case_id == "C-1"
    assert str(cases[0].value).lower() == "yes"


def test_excel_provider(tmp_path):
    path = tmp_path / "cases.xlsx"
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["case_id", "value"])
    sheet.append(["C-1", "yes"])
    workbook.save(path)
    assert DataLoader.load(path, model=Case)[0].value == "yes"


def test_duplicate_case_id_has_row_context(tmp_path):
    path = tmp_path / "cases.csv"
    path.write_text("case_id,value\nC-1,a\nC-1,b\n", encoding="utf-8")
    with pytest.raises(DataValidationError, match="row 3, duplicate case_id"):
        DataLoader.load(path)


def test_secret_placeholder_not_resolved_during_collection(tmp_path):
    path = tmp_path / "cases.json"
    path.write_text('[{"case_id":"C-1","value":"${QA_PASSWORD}"}]', encoding="utf-8")
    case = DataLoader.load(path)[0]
    assert case["value"] == "${QA_PASSWORD}"
    with pytest.raises(MissingVariableError, match="QA_PASSWORD"):
        resolve_runtime_variables(case, environ={})
    resolved = resolve_runtime_variables(case, environ={"QA_PASSWORD": "hidden"})
    assert "hidden" not in repr(resolved)


def test_unsupported_extension(tmp_path):
    path = tmp_path / "cases.xml"
    path.write_text("<cases/>", encoding="utf-8")
    with pytest.raises(UnsupportedDataFormatError):
        DataLoader.load(path)
