import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from qa_framework.postman.command_builder import build_command
from qa_framework.postman.result import PostmanStatus
from qa_framework.postman.runner import PostmanRunner

pytestmark = [pytest.mark.framework, pytest.mark.unit]


def test_command_is_argument_list_and_local_reporting(tmp_path):
    collection = tmp_path / "collection.json"
    collection.write_text("{}", encoding="utf-8")
    command = build_command("postman", collection, tmp_path)
    assert isinstance(command, list)
    assert "--no-report-events" in command
    assert "shell=True" not in command


def test_runner_maps_nonzero_exit_and_redacts(monkeypatch, tmp_path):
    collection = tmp_path / "collection.json"
    collection.write_text("{}", encoding="utf-8")
    monkeypatch.setattr("shutil.which", lambda _name: "/bin/postman")
    monkeypatch.setattr(
        "subprocess.run",
        lambda *_args, **_kwargs: SimpleNamespace(
            returncode=1, stdout="token=swordfish", stderr="failed"
        ),
    )
    result = PostmanRunner(secrets=("swordfish",)).run(collection, tmp_path / "reports")
    assert result.status is PostmanStatus.FAILED
    assert "swordfish" not in result.stdout_summary


def test_runner_uses_temporary_local_environment_for_variables(monkeypatch, tmp_path):
    collection = tmp_path / "collection.json"
    collection.write_text("{}", encoding="utf-8")
    observed = {}

    def fake_run(command, **_kwargs):
        observed["command"] = command
        environment_path = Path(command[command.index("-e") + 1])
        observed["environment_path"] = environment_path
        observed["environment"] = json.loads(environment_path.read_text(encoding="utf-8"))
        return SimpleNamespace(returncode=0, stdout="ok", stderr="")

    monkeypatch.setattr("shutil.which", lambda _name: "/bin/postman")
    monkeypatch.setattr("subprocess.run", fake_run)
    result = PostmanRunner().run(
        collection,
        tmp_path / "reports",
        variables={"baseUrl": "http://127.0.0.1", "token": "temporary-secret"},
    )

    assert result.status is PostmanStatus.PASSED
    assert "--env-var" not in observed["command"]
    assert observed["environment"]["values"][1]["value"] == "temporary-secret"
    assert not observed["environment_path"].exists()
