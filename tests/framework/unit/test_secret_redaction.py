import logging

import pytest

from qa_framework.config import SecretValue
from qa_framework.logging.redaction import Redactor, environment_secrets, redact, redact_url

pytestmark = [pytest.mark.framework, pytest.mark.unit]


def test_secret_value_never_repr_or_str_plaintext():
    secret = SecretValue("swordfish")
    assert "swordfish" not in repr(secret)
    assert "swordfish" not in str(secret)
    assert secret.reveal() == "swordfish"


def test_nested_redaction_and_url_query():
    assert redact({"password": "plain", "nested": {"token": "abc"}}) == {
        "password": "********",
        "nested": {"token": "********"},
    }
    clean = redact_url("https://example.test/path?token=abc&safe=yes")
    assert "abc" not in clean
    assert "safe=yes" in clean


def test_logging_filter_removes_registered_secret():
    record = logging.LogRecord("test", logging.INFO, __file__, 1, "value swordfish", (), None)
    assert Redactor(("swordfish",)).filter(record)
    assert "swordfish" not in record.getMessage()


def test_environment_secret_discovery_only_registers_sensitive_useful_values():
    secrets = environment_secrets(
        {
            "QA_PASSWORD": "swordfish",
            "PUBLIC_NAME": "safe",
            "TINY_TOKEN": "abc",
            "EMPTY_SECRET": "",
        }
    )
    assert secrets == ("swordfish",)
    assert "swordfish" not in redact("failure exposed swordfish", secrets)
