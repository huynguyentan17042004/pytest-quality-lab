import json
from pathlib import Path

import pytest

from qa_framework.api.schema_validator import validate_schema
from tests.support.api_clients.posts_client import PostsClient

pytestmark = [
    pytest.mark.demo,
    pytest.mark.api,
    pytest.mark.smoke,
    pytest.mark.external,
    pytest.mark.serial,
]


@pytest.fixture
def posts_client(settings, api_session):
    assert settings.api_base_url == "https://jsonplaceholder.typicode.com", (
        "external API host is not allowlisted"
    )
    return PostsClient(settings.api_base_url, api_session, settings.timeout)


def test_get_single_post(posts_client):
    response = posts_client.get_post(1)
    assert response.status_code == 200
    payload = response.json()
    schema = json.loads(
        (Path(__file__).parents[2] / "schemas" / "api" / "post.schema.json").read_text()
    )
    validate_schema(payload, schema)
    assert payload["id"] == 1
    assert isinstance(payload["title"], str) and payload["title"].strip()
    assert isinstance(payload["body"], str) and payload["body"].strip()


test_get_single_post.case_id = "DEMO-API-001"
