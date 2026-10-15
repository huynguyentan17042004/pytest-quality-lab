import json
from pathlib import Path

import pytest

from qa_framework.api.schema_validator import validate_schema
from tests.support.api_clients.posts_client import PostsClient

pytestmark = [pytest.mark.demo, pytest.mark.api, pytest.mark.integration]


@pytest.fixture
def local_posts_client(local_api_server, api_session, settings):
    return PostsClient(local_api_server, api_session, settings.timeout)


@pytest.mark.requirement("REQ-API-POST-READ")
def test_local_post_contract(local_posts_client):
    response = local_posts_client.get_post(1)
    schema_path = Path(__file__).parents[2] / "schemas" / "api" / "post.schema.json"
    validate_schema(response.json(), json.loads(schema_path.read_text(encoding="utf-8")))
    assert response.status_code == 200
    assert response.json()["title"] == "Controlled local post"


test_local_post_contract.case_id = "DEMO-LOCAL-API-001"


@pytest.mark.requirement("REQ-API-POST-NOT-FOUND")
def test_local_missing_post_is_expected_negative(local_posts_client):
    response = local_posts_client.get_post(999)
    assert response.status_code == 404
    assert response.json() == {"error": "post not found"}


test_local_missing_post_is_expected_negative.case_id = "DEMO-LOCAL-API-002"
