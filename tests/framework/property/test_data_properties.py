from pathlib import Path

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from qa_framework.data.validators import validate_rows
from qa_framework.logging.redaction import redact

pytestmark = [pytest.mark.framework, pytest.mark.property]


@settings(max_examples=60, derandomize=True)
@given(st.lists(st.text(min_size=1), min_size=1, max_size=30, unique=True))
def test_unique_case_ids_are_always_accepted(case_ids):
    validate_rows(
        [{"case_id": case_id, "value": index} for index, case_id in enumerate(case_ids)],
        Path("generated.json"),
    )


@settings(max_examples=60, derandomize=True)
@given(
    st.text(alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd")), min_size=4),
    st.text(),
)
@pytest.mark.requirement("REQ-FRAMEWORK-REDACTION")
def test_registered_secret_never_survives_redaction(secret, surrounding):
    assert secret not in redact(f"{surrounding}{secret}{surrounding}", (secret,))
