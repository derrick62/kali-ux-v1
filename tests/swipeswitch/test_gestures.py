from kali_ux.features.window_switcher.engine.events import GestureEvent
from kali_ux.features.window_switcher.engine.gestures import GestureRecognizer


def event(kind, fingers, dx=0, dy=0, cancelled=False):
    return GestureEvent(kind, fingers, dx, dy, cancelled)


def test_three_finger_left_starts_switch_and_advances_steps():
    recognizer = GestureRecognizer(threshold_px=30, step_px=50)
    assert recognizer.handle(event("begin", 3)) == []
    actions = recognizer.handle(event("update", 3, dx=-110))
    assert [action.name for action in actions] == ["switch_begin", "switch_move"]
    assert actions[0].direction == "left"
    assert actions[1].steps == 2
    assert recognizer.handle(event("end", 3))[0].name == "switch_commit"


def test_three_finger_up_routes_to_task_view():
    recognizer = GestureRecognizer(threshold_px=25)
    recognizer.handle(event("begin", 3))
    recognizer.handle(event("update", 3, dy=-40))
    actions = recognizer.handle(event("end", 3))
    assert [(a.name, a.direction) for a in actions] == [("task_view", "up")]


def test_three_finger_down_routes_to_show_desktop():
    recognizer = GestureRecognizer(threshold_px=25)
    recognizer.handle(event("begin", 3))
    recognizer.handle(event("update", 3, dy=40))
    actions = recognizer.handle(event("end", 3))
    assert [a.name for a in actions] == ["show_desktop"]


def test_four_finger_left_navigates_next_workspace():
    recognizer = GestureRecognizer(threshold_px=25)
    recognizer.handle(event("begin", 4))
    actions = recognizer.handle(event("update", 4, dx=-90))
    assert [(a.name, a.direction, a.steps) for a in actions] == [("workspace", "left", 1)]
    assert recognizer.handle(event("end", 4)) == []


def test_four_finger_short_flick_moves_one_workspace_on_release():
    recognizer = GestureRecognizer(threshold_px=25, step_px=80)
    recognizer.handle(event("begin", 4))
    assert recognizer.handle(event("update", 4, dx=45)) == []
    actions = recognizer.handle(event("end", 4))
    assert [(a.name, a.direction, a.steps) for a in actions] == [("workspace", "right", 1)]


def test_four_finger_reversal_routes_each_crossed_workspace_step():
    recognizer = GestureRecognizer(threshold_px=20, step_px=40)
    recognizer.handle(event("begin", 4))
    recognizer.handle(event("update", 4, dx=-50))
    actions = recognizer.handle(event("update", 4, dx=100))
    assert [(a.name, a.direction, a.steps) for a in actions] == [("workspace", "right", 2)]


def test_cancelled_horizontal_switch_never_commits():
    recognizer = GestureRecognizer(threshold_px=25)
    recognizer.handle(event("begin", 3))
    recognizer.handle(event("update", 3, dx=-40))
    actions = recognizer.handle(event("end", 3, cancelled=True))
    assert [a.name for a in actions] == ["switch_cancel"]


def test_ambiguous_diagonal_gesture_is_ignored():
    recognizer = GestureRecognizer(threshold_px=25)
    recognizer.handle(event("begin", 3))
    recognizer.handle(event("update", 3, dx=35, dy=30))
    assert recognizer.handle(event("end", 3)) == []


def test_horizontal_reversal_changes_selection_direction():
    recognizer = GestureRecognizer(threshold_px=20, step_px=40)
    recognizer.handle(event("begin", 3))
    recognizer.handle(event("update", 3, dx=-50))
    actions = recognizer.handle(event("update", 3, dx=100))
    movement = [a for a in actions if a.name == "switch_move"]
    assert movement
    assert movement[-1].direction == "right"
    # The pointer crossed back over the original left step and one step to
    # the right, so two rightward selection steps correctly undo and reverse.
    assert movement[-1].steps == 2


def test_finger_count_change_cancels_active_switch_immediately():
    recognizer = GestureRecognizer(threshold_px=20, step_px=40)
    recognizer.handle(event("begin", 3))
    recognizer.handle(event("update", 3, dx=-45))
    actions = recognizer.handle(event("update", 4, dx=-10))
    assert [action.name for action in actions] == ["switch_cancel"]
    assert recognizer.handle(event("end", 4)) == []


def test_new_begin_cancels_previous_unfinished_switch():
    recognizer = GestureRecognizer(threshold_px=20, step_px=40)
    recognizer.handle(event("begin", 3))
    recognizer.handle(event("update", 3, dx=-45))
    actions = recognizer.handle(event("begin", 4))
    assert [action.name for action in actions] == ["switch_cancel"]
    actions = recognizer.handle(event("update", 4, dx=-40))
    assert [(action.name, action.direction) for action in actions] == [("workspace", "left")]
    assert recognizer.handle(event("end", 4)) == []


def test_timeout_cancels_switch_without_committing():
    recognizer = GestureRecognizer(threshold_px=20, step_px=40)
    recognizer.handle(event("begin", 3))
    recognizer.handle(event("update", 3, dx=-45))
    recognizer.last_activity -= 10
    actions = recognizer.check_timeout(1)
    assert [action.name for action in actions] == ["switch_cancel"]
    assert recognizer.handle(event("end", 3)) == []


def test_invert_direction_reverses_horizontal_switch_steps():
    recognizer = GestureRecognizer(threshold_px=20, step_px=40, invert_direction=True)
    recognizer.handle(event("begin", 3))
    recognizer.handle(event("update", 3, dx=-50))
    actions = recognizer.handle(event("update", 3, dx=-40))
    assert [(action.name, action.direction, action.steps) for action in actions] == [
        ("switch_move", "right", 1)
    ]


def test_four_finger_flick_respects_configured_minimum_distance():
    recognizer = GestureRecognizer(threshold_px=20, flick_min_px=50, step_px=100)
    recognizer.handle(event("begin", 4))
    recognizer.handle(event("update", 4, dx=30))
    assert recognizer.handle(event("end", 4)) == []
