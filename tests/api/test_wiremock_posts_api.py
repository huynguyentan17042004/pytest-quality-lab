"""Business-oriented HTTP virtualization tests managed entirely by pytest."""

import json

import pytest
import requests

from qa_framework.api import BaseApiClient
from qa_framework.api.schema_validator import validate_schema
from qa_framework.exceptions import ApiTimeoutError, ApiTransportError
from tests.support.api_clients.posts_client import PostsClient

pytestmark = [
    pytest.mark.api,
    pytest.mark.integration,
    pytest.mark.demo,
    pytest.mark.serial,
]


@pytest.fixture
def wiremock_posts_client(isolated_wiremock, settings, api_session):
    return PostsClient(settings.api_base_url, api_session, settings.timeout)


def load_schema(settings, name: str) -> dict:
    path = settings.project_root / "schemas" / "api" / name
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.mark.requirement("REQ-API-POST-READ")
def test_wiremock_post_matches_shared_schema(wiremock_posts_client, isolated_wiremock, settings):
    response = wiremock_posts_client.get_post(1)

    assert response.status_code == 200
    payload = response.json()
    validate_schema(payload, load_schema(settings, "post.schema.json"))
    assert payload == {
        "userId": 7,
        "id": 1,
        "title": "Controlled local post",
        "body": "Deterministic contract fixture",
    }
    assert isolated_wiremock.request_count({"method": "GET", "urlPath": "/posts/1"}) == 1


test_wiremock_post_matches_shared_schema.case_id = "DEMO-WIREMOCK-API-001"


@pytest.mark.requirement("REQ-API-POST-NOT-FOUND")
def test_wiremock_unknown_post_returns_typed_error(
    wiremock_posts_client, isolated_wiremock, settings
):
    response = wiremock_posts_client.get_post(999)

    assert response.status_code == 404
    payload = response.json()
    validate_schema(payload, load_schema(settings, "error.schema.json"))
    assert payload == {"error": "post not found"}
    assert isolated_wiremock.request_count({"method": "GET", "urlPath": "/posts/999"}) == 1


test_wiremock_unknown_post_returns_typed_error.case_id = "DEMO-WIREMOCK-API-002"


@pytest.mark.requirement("REQ-API-POST-UNAVAILABLE")
def test_wiremock_service_unavailable_is_not_retried(
    wiremock_posts_client, isolated_wiremock, settings
):
    response = wiremock_posts_client.get_post(503)

    assert response.status_code == 503
    payload = response.json()
    validate_schema(payload, load_schema(settings, "error.schema.json"))
    assert payload == {"error": "service unavailable"}
    assert isolated_wiremock.request_count({"method": "GET", "urlPath": "/posts/503"}) == 1


test_wiremock_service_unavailable_is_not_retried.case_id = "DEMO-WIREMOCK-API-003"


@pytest.mark.requirement("REQ-API-POST-FILTER")
def test_wiremock_matches_business_filters_and_correlation_header(
    isolated_wiremock, settings, api_session
):
    isolated_wiremock.add_stub(
        {
            "priority": 1,
            "request": {
                "method": "GET",
                "urlPath": "/posts",
                "queryParameters": {"userId": {"equalTo": "7"}, "limit": {"equalTo": "2"}},
                "headers": {"X-Correlation-ID": {"matches": "qa-[0-9]+"}},
            },
            "response": {
                "status": 200,
                "headers": {"Content-Type": "application/json"},
                "jsonBody": [{"id": 1}, {"id": 2}],
            },
        }
    )
    client = BaseApiClient(settings.api_base_url, session=api_session, request_budget=1)

    response = client.get(
        "/posts", params={"userId": 7, "limit": 2}, headers={"X-Correlation-ID": "qa-42"}
    )

    assert response.status_code == 200
    assert response.json() == [{"id": 1}, {"id": 2}]
    assert (
        isolated_wiremock.request_count(
            {
                "method": "GET",
                "urlPath": "/posts",
                "queryParameters": {"userId": {"equalTo": "7"}, "limit": {"equalTo": "2"}},
                "headers": {"X-Correlation-ID": {"equalTo": "qa-42"}},
            }
        )
        == 1
    )


test_wiremock_matches_business_filters_and_correlation_header.case_id = "DEMO-WIREMOCK-API-004"


@pytest.mark.requirement("REQ-API-POST-CREATE")
@pytest.mark.parametrize(
    ("payload", "expected_status", "expected_body"),
    [
        pytest.param(
            {"userId": 7, "title": "Deep mocking", "body": "Validated request"},
            201,
            {"id": 101, "status": "created"},
            id="valid-payload",
        ),
        pytest.param(
            {"userId": 7, "title": "", "body": "Missing business title"},
            422,
            {"error": "title must not be blank"},
            id="blank-title",
        ),
    ],
)
def test_wiremock_create_post_business_validation(
    isolated_wiremock, settings, api_session, payload, expected_status, expected_body
):
    isolated_wiremock.add_stub(
        {
            "priority": 1,
            "request": {
                "method": "POST",
                "urlPath": "/posts",
                "headers": {"Content-Type": {"contains": "application/json"}},
                "bodyPatterns": [
                    {"matchesJsonPath": "$[?(@.title =~ /.+/)]"},
                    {"matchesJsonPath": "$[?(@.userId == 7)]"},
                ],
            },
            "response": {
                "status": 201,
                "headers": {"Content-Type": "application/json"},
                "jsonBody": {"id": 101, "status": "created"},
            },
        }
    )
    isolated_wiremock.add_stub(
        {
            "priority": 10,
            "request": {"method": "POST", "urlPath": "/posts"},
            "response": {
                "status": 422,
                "headers": {"Content-Type": "application/json"},
                "jsonBody": {"error": "title must not be blank"},
            },
        }
    )
    client = BaseApiClient(settings.api_base_url, session=api_session, request_budget=1)

    response = client.request("POST", "/posts", json=payload)

    assert response.status_code == expected_status
    assert response.json() == expected_body
    assert isolated_wiremock.request_count({"method": "POST", "urlPath": "/posts"}) == 1


test_wiremock_create_post_business_validation.case_id = "DEMO-WIREMOCK-API-005"


@pytest.mark.requirement("REQ-API-POST-RETRY")
def test_wiremock_transient_failure_recovers_with_one_retry(
    isolated_wiremock, settings, api_session
):
    isolated_wiremock.add_stub(
        {
            "priority": 1,
            "scenarioName": "transient-post-read",
            "requiredScenarioState": "Started",
            "newScenarioState": "Recovered",
            "request": {"method": "GET", "urlPath": "/posts/transient"},
            "response": {
                "status": 503,
                "headers": {"Content-Type": "application/json"},
                "jsonBody": {"error": "temporary outage"},
            },
        }
    )
    isolated_wiremock.add_stub(
        {
            "priority": 1,
            "scenarioName": "transient-post-read",
            "requiredScenarioState": "Recovered",
            "request": {"method": "GET", "urlPath": "/posts/transient"},
            "response": {
                "status": 200,
                "headers": {"Content-Type": "application/json"},
                "jsonBody": {
                    "userId": 7,
                    "id": 88,
                    "title": "Recovered post",
                    "body": "Second attempt succeeded",
                },
            },
        }
    )
    client = BaseApiClient(
        settings.api_base_url,
        session=api_session,
        timeout=1,
        retry_count=1,
        request_budget=2,
    )

    response = client.get("/posts/transient")

    assert response.status_code == 200
    validate_schema(response.json(), load_schema(settings, "post.schema.json"))
    assert isolated_wiremock.request_count({"method": "GET", "urlPath": "/posts/transient"}) == 2


test_wiremock_transient_failure_recovers_with_one_retry.case_id = "DEMO-WIREMOCK-API-006"


@pytest.mark.requirement("REQ-API-POST-TIMEOUT")
def test_wiremock_slow_dependency_becomes_domain_timeout(isolated_wiremock, settings, api_session):
    isolated_wiremock.add_stub(
        {
            "priority": 1,
            "request": {"method": "GET", "urlPath": "/posts/slow"},
            "response": {
                "status": 200,
                "fixedDelayMilliseconds": 750,
                "headers": {"Content-Type": "application/json"},
                "jsonBody": {"status": "slow"},
            },
        }
    )
    client = BaseApiClient(
        settings.api_base_url, session=api_session, timeout=0.1, request_budget=1
    )

    with pytest.raises(ApiTimeoutError, match="timed out"):
        client.get("/posts/slow")

    assert isolated_wiremock.request_count({"method": "GET", "urlPath": "/posts/slow"}) == 1


test_wiremock_slow_dependency_becomes_domain_timeout.case_id = "DEMO-WIREMOCK-API-007"


@pytest.mark.requirement("REQ-API-POST-MALFORMED")
def test_wiremock_malformed_json_is_visible_to_the_consumer(
    isolated_wiremock, settings, api_session
):
    isolated_wiremock.add_stub(
        {
            "priority": 1,
            "request": {"method": "GET", "urlPath": "/posts/malformed"},
            "response": {
                "status": 200,
                "headers": {"Content-Type": "application/json"},
                "body": "{not-valid-json",
            },
        }
    )
    client = BaseApiClient(settings.api_base_url, session=api_session, request_budget=1)

    response = client.get("/posts/malformed")

    assert response.status_code == 200
    with pytest.raises(requests.exceptions.JSONDecodeError):
        response.json()


test_wiremock_malformed_json_is_visible_to_the_consumer.case_id = "DEMO-WIREMOCK-API-008"


@pytest.mark.requirement("REQ-API-POST-TRANSPORT")
def test_wiremock_empty_connection_becomes_transport_error(
    isolated_wiremock, settings, api_session
):
    isolated_wiremock.add_stub(
        {
            "priority": 1,
            "request": {"method": "GET", "urlPath": "/posts/connection-fault"},
            "response": {"fault": "EMPTY_RESPONSE"},
        }
    )
    client = BaseApiClient(settings.api_base_url, session=api_session, timeout=1, request_budget=1)

    with pytest.raises(ApiTransportError, match="transport failed"):
        client.get("/posts/connection-fault")

    assert (
        isolated_wiremock.request_count({"method": "GET", "urlPath": "/posts/connection-fault"})
        == 1
    )


test_wiremock_empty_connection_becomes_transport_error.case_id = "DEMO-WIREMOCK-API-009"
