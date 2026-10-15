import pytest

from qa_framework.assertions import SoftAssertions

pytestmark = [pytest.mark.framework, pytest.mark.unit]


def test_soft_assertions_collect_and_reset():
    softly = SoftAssertions()
    softly.check(False, "first")
    softly.check(False, "second")
    with pytest.raises(AssertionError, match="first"):
        softly.assert_all()
    assert softly.errors == ()
