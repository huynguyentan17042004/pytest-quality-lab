import json

import pytest

pytestmark = [pytest.mark.framework, pytest.mark.unit]


def _project(pytester):
    config_dir = pytester.path / "configs" / "environments"
    config_dir.mkdir(parents=True)
    (config_dir / "local.toml").write_text(
        'environment="local"\napi_base_url="http://127.0.0.1"\nui_base_url="file:///"\nbrowser="chrome"\ntimeout=2\nheadless=true\nretry_count=0\n',
        encoding="utf-8",
    )
    pytester.makeconftest('pytest_plugins=["qa_framework.pytest_plugin.plugin"]')


def test_external_test_is_skipped_without_opt_in(pytester):
    _project(pytester)
    pytester.makepyfile(
        test_demo="""
import pytest
@pytest.mark.external
@pytest.mark.demo
def test_live():
    assert False
test_live.case_id = "DEMO-API-001"
"""
    )
    result = pytester.runpytest("-q")
    result.assert_outcomes(skipped=1)


def test_unapproved_external_case_fails_closed(pytester):
    _project(pytester)
    pytester.makepyfile(
        test_demo="""
import pytest
@pytest.mark.external
def test_live(): pass
test_live.case_id = "UNKNOWN"
"""
    )
    result = pytester.runpytest("--run-external", "-q")
    assert result.ret != 0
    result.stderr.fnmatch_lines(["*external case is not approved*"])


def test_plugin_writes_summary_and_manifest(pytester):
    _project(pytester)
    pytester.makepyfile("def test_ok(): assert True")
    result = pytester.runpytest("-q")
    result.assert_outcomes(passed=1)
    manifests = list(pytester.path.glob("artifacts/runs/*/manifest.json"))
    assert len(manifests) == 1
    assert json.loads(manifests[0].read_text())["counts"]["passed"] == 1


def test_collect_only_does_not_create_analytics_run(pytester):
    _project(pytester)
    pytester.makepyfile("def test_ok(): assert True")
    result = pytester.runpytest("--collect-only", "-q")
    assert result.ret == 0
    assert not (pytester.path / "artifacts/analytics/quality.db").exists()


def test_failure_log_redacts_secret_discovered_from_environment(pytester, monkeypatch):
    secret = "traceback-secret-12345"
    monkeypatch.setenv("QA_PASSWORD", secret)
    _project(pytester)
    pytester.makepyfile(
        test_failure=f'def test_failure(): raise AssertionError("exposed {secret}")'
    )

    result = pytester.runpytest("-q", "--no-analytics")
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines(["*AssertionError: exposed *********"])
