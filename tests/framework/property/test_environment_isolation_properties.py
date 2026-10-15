import os

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from qa_framework.config import EnvironmentSandbox

pytestmark = [pytest.mark.framework, pytest.mark.property]

ENVIRONMENTS = st.dictionaries(
    keys=st.from_regex(r"QA_PROP_[A-Z]{1,8}", fullmatch=True),
    values=st.text(
        alphabet=st.characters(blacklist_characters="\x00", blacklist_categories=("Cs",)),
        max_size=40,
    ),
    max_size=8,
)


@settings(max_examples=40, derandomize=True)
@given(ENVIRONMENTS)
@pytest.mark.requirement("REQ-FRAMEWORK-ENV-ISOLATION")
def test_environment_is_restored_for_generated_overrides(overrides):
    before = dict(os.environ)
    with EnvironmentSandbox(overrides):
        assert all(os.environ[key] == value for key, value in overrides.items())
    assert dict(os.environ) == before
