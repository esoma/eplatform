import pytest

from eplatform import Controller
from eplatform import Platform
from eplatform import get_controllers
from eplatform._eplatform import connect_virtual_joystick
from eplatform._eplatform import disconnect_virtual_joystick


class VirtualController:
    def __init__(self):
        self.sdl_joystick = None
        self.name = "Virtual Joystick"
        self.connect()

    def connect(self):
        self.sdl_joystick = connect_virtual_joystick(self.name)

    def disconnect(self):
        disconnect_virtual_joystick(self.sdl_joystick)
        self.sdl_joystick = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, *args, **kwargs):
        self.disconnect()

    def get_controller(self):
        for controller in get_controllers():
            if controller._sdl_joystick == self.sdl_joystick:
                assert controller.is_connected
                assert controller.name == self.name
                return controller
        return None


@pytest.mark.parametrize("count", [0, 1, 5])
def test_discover_controllers(count):
    vcs = [VirtualController() for i in range(count)]
    with Platform():
        assert set(get_controllers()) == {vc.get_controller() for vc in vcs}


@pytest.mark.parametrize("event_object", [Controller, None])
@pytest.mark.parametrize(
    "disconnected_event_name, connected_event_name",
    [("connection_changed", "connection_changed"), ("disconnected", "connected")],
)
def test_connect_disconnect(
    capture_event, event_object, disconnected_event_name, connected_event_name
):
    vc = VirtualController()
    with Platform():
        controller1 = vc.get_controller()
        assert set(get_controllers()) == {controller1}

        def _():
            vc.disconnect()

        event = capture_event(_, getattr(event_object or controller1, disconnected_event_name))
        assert event == {"controller": controller1, "is_connected": False}
        assert not controller1.is_connected
        assert not set(get_controllers())

        def _():
            vc.connect()

        event = capture_event(_, getattr(Controller, connected_event_name))
        controller2 = vc.get_controller()
        assert controller1 is not controller2
        assert event == {"controller": controller2, "is_connected": True}
        assert not controller1.is_connected
        assert controller2.is_connected
        assert set(get_controllers()) == {controller2}
