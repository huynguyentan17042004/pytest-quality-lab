import pytest

from qa_framework.testdata import ResourceTracker

pytestmark = [pytest.mark.framework, pytest.mark.unit]


def test_cleanup_is_lifo_best_effort_and_idempotent():
    events = []
    tracker = ResourceTracker()
    tracker.register(events.append, "first")
    tracker.register(lambda: (_ for _ in ()).throw(RuntimeError("broken")))
    tracker.register(events.append, "last")
    errors = tracker.cleanup()
    assert events == ["last", "first"]
    assert len(errors) == 1
    assert tracker.cleanup() == []
