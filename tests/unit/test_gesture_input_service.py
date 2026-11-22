from kali_ux.features.gesture_control import service as input_service
from kali_ux.features.window_switcher.engine.events import GestureEvent


def test_input_service_fans_out_normalized_events():
    service = input_service.GestureInputService()
    received_a = []
    received_b = []
    callback_a = received_a.append
    callback_b = received_b.append
    service.subscribe(callback_a)
    service.subscribe(callback_a)
    service.subscribe(callback_b)

    event = GestureEvent("update", fingers=3, dx=-12.5)
    service._publish(event)
    service.unsubscribe(callback_a)
    service._publish(GestureEvent("end", fingers=3))

    assert received_a == [event]
    assert received_b == [event, GestureEvent("end", fingers=3)]


def test_input_service_stops_listener_and_is_idempotent():
    class Listener:
        def __init__(self):
            self.stopped = 0

        def stop(self):
            self.stopped += 1

    service = input_service.GestureInputService()
    listener = Listener()
    service._listener = listener
    service.stop()
    service.stop()
    assert listener.stopped == 1
    assert not service.running


def test_input_service_starts_one_listener_with_configured_motion_mode(monkeypatch):
    class Listener:
        def __init__(self, device, fingers, callback, *, debug, use_unaccelerated):
            self.device = device
            self.fingers = fingers
            self.callback = callback
            self.debug = debug
            self.use_unaccelerated = use_unaccelerated
            self.started = False

        def start(self):
            self.started = True

        def stop(self):
            self.started = False

    monkeypatch.setattr(input_service.os, "access", lambda *_args: True)
    monkeypatch.setattr(
        "kali_ux.features.gesture_control.conflicts.inspect_gesture_providers", lambda: []
    )
    service = input_service.GestureInputService(
        "/dev/input/event4", debug=True, use_unaccelerated=True, listener_factory=Listener
    )
    service.subscribe(lambda _event: None)
    assert service.start() == "/dev/input/event4"
    assert service.running
    assert service._listener.started
    assert service._listener.use_unaccelerated is True
    service.set_use_unaccelerated(False)
    assert service._listener.use_unaccelerated is False
    service.stop()
    assert not service.running


def test_input_service_refuses_unreadable_device_without_changing_permissions(monkeypatch):
    monkeypatch.setattr(input_service.os, "access", lambda *_args: False)
    service = input_service.GestureInputService("/dev/input/event4")
    import pytest

    with pytest.raises(PermissionError, match="will not change"):
        service.start()
