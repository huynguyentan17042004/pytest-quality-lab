from datetime import timedelta

import pytest
import requests

from qa_framework.api.base_client import BaseApiClient
from qa_framework.api.response_mapper import ResponseMapper
from qa_framework.exceptions import ApiTimeoutError, ApiTransportError, ResponseParseError

pytestmark = [pytest.mark.framework, pytest.mark.unit, pytest.mark.api]


def response(status=200, body=b'{"ok": true}', content_type="application/json"):
    item = requests.Response()
    item.status_code = status
    item._content = body
    item.headers["Content-Type"] = content_type
    item.elapsed = timedelta(milliseconds=20)
    return item


class FakeSession:
    def __init__(self, outcomes):
        self.outcomes = iter(outcomes)
        self.headers = {}
        self.closed = False

    def request(self, *_args, **_kwargs):
        outcome = next(self.outcomes)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome

    def close(self):
        self.closed = True


def test_request_uses_injected_transport_and_preserves_raw():
    raw = response()
    session = FakeSession([raw])
    client = BaseApiClient("https://example.test", session=session, timeout=3)
    assert client.get("/status") is raw
    mapped = ResponseMapper.map(raw)
    assert mapped.json() == {"ok": True}
    assert mapped.raw is raw


def test_204_has_no_body():
    assert ResponseMapper.map(response(204, b"", "")).body is None


def test_malformed_json_is_classified():
    with pytest.raises(ResponseParseError, match="declared JSON"):
        ResponseMapper.map(response(body=b"not-json"))


def test_timeout_is_wrapped_with_cause():
    client = BaseApiClient(
        "https://example.test", session=FakeSession([requests.Timeout("secret")])
    )
    with pytest.raises(ApiTimeoutError) as caught:
        client.get("/slow")
    assert isinstance(caught.value.__cause__, requests.Timeout)


def test_retry_is_limited_to_idempotent_transient_response():
    session = FakeSession([response(503), response(200)])
    client = BaseApiClient("https://example.test", session=session, retry_count=1)
    assert client.get("/resource").status_code == 200
    assert client.attempts == 2


def test_request_budget_fails_before_extra_call():
    client = BaseApiClient(
        "https://example.test", session=FakeSession([response()]), request_budget=0
    )
    with pytest.raises(ApiTransportError, match="budget"):
        client.get("/resource")
