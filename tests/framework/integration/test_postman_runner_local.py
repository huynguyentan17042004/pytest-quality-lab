import json
import shutil
from pathlib import Path

import pytest

from qa_framework.postman import PostmanRunner, PostmanStatus

pytestmark = [pytest.mark.framework, pytest.mark.integration, pytest.mark.api]


def test_local_collection_when_postman_cli_is_available(local_api_server, tmp_path):
    if not shutil.which("postman"):
        pytest.skip("Postman CLI is not installed; mocked runner contract remains mandatory")

    environment = tmp_path / "local.postman_environment.json"
    environment.write_text(
        json.dumps(
            {
                "name": "controlled-local",
                "values": [{"key": "baseUrl", "value": local_api_server, "enabled": True}],
            }
        ),
        encoding="utf-8",
    )
    collection = (
        Path(__file__).parents[3]
        / "postman"
        / "collections"
        / "local-health.postman_collection.json"
    )
    result = PostmanRunner(timeout=30).run(
        collection,
        tmp_path / "postman-reports",
        environment=environment,
    )
    assert result.status is PostmanStatus.PASSED
    assert result.exit_code == 0
