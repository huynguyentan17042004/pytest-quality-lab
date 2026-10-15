import os

import pytest

pytestmark = [pytest.mark.framework, pytest.mark.unit]


def test_isolated_env_fixture_restores_changes(isolated_env):
    original = os.environ.get("QA_ISOLATED_TEST")
    isolated_env.set("QA_ISOLATED_TEST", "temporary")
    assert os.environ["QA_ISOLATED_TEST"] == "temporary"
    isolated_env.unset("QA_ISOLATED_TEST")
    assert "QA_ISOLATED_TEST" not in os.environ
    if original is not None:
        isolated_env.set("QA_ISOLATED_TEST", original)
