import pytest

from qa_framework.reporting.artifact_manager import ArtifactManager

pytestmark = [pytest.mark.framework, pytest.mark.integration]


class BrokenDriver:
    page_source = "<html><body>password=swordfish</body></html>"

    def save_screenshot(self, _path):
        raise RuntimeError("capture broke")


def test_artifact_capture_failure_does_not_raise(tmp_path):
    manager = ArtifactManager(tmp_path)
    paths = manager.capture_webdriver_failure("case::id", BrokenDriver())
    assert len(paths) == 1
    assert paths[0].suffix == ".html"


def test_artifact_size_is_capped(tmp_path):
    manager = ArtifactManager(tmp_path, max_bytes=10)
    path = manager.write_text("api_exchanges", "body.txt", "x" * 100)
    assert path.stat().st_size == 10
