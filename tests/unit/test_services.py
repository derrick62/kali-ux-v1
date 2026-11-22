from kali_ux.features.clipboard_history.service import ClipboardHistory
from kali_ux.features.snap_assist.service import PRESETS


def test_clipboard_history_deduplicates_and_bounds():
    h = ClipboardHistory(max_items=2)
    assert h.add("one") and h.add("two") and h.add("three")
    assert [x.text for x in h.search()] == ["three", "two"]
    assert not h.add("three")
    assert not h.add("secret", sensitive=True)
    h.clear()
    assert h.search() == []


def test_snap_presets_are_normalized():
    assert len(PRESETS) == 8
    assert all(0 <= x <= 1 for p in PRESETS.values() for x in p)


def test_gesture_action_router_routes_each_action_once():
    from types import SimpleNamespace

    from kali_ux.features.gesture_control.router import GestureActionRouter

    router = GestureActionRouter()
    seen = []
    router.register("switch_move", seen.append)
    action = SimpleNamespace(name="switch_move", steps=2)
    assert router.dispatch(action)
    assert seen == [action]
    assert not router.dispatch(SimpleNamespace(name="unknown"))


def test_gesture_action_router_rejects_duplicate_handlers():
    import pytest

    from kali_ux.features.gesture_control.router import GestureActionRouter

    router = GestureActionRouter()
    router.register("task_view", lambda _action: None)
    with pytest.raises(ValueError, match="already registered"):
        router.register("task_view", lambda _action: None)
