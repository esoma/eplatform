from math import isclose
from unittest.mock import ANY
from uuid import uuid4

import pytest

from eplatform import Controller
from eplatform import ControllerAxis
from eplatform import ControllerBall
from eplatform import ControllerButton
from eplatform import ControllerHat
from eplatform import Platform
from eplatform import get_controllers
from eplatform._eplatform import connect_virtual_joystick
from eplatform._eplatform import disconnect_virtual_joystick
from eplatform._eplatform import set_virtual_joystick_axis_position


class VirtualController:
    def __init__(self, *, name=None, axis_count=0, ball_count=0, button_count=0, hat_count=0):
        self.sdl_joystick = None
        self.name = name or uuid4().hex
        self.axis_count = axis_count
        self.ball_count = ball_count
        self.button_count = button_count
        self.hat_count = hat_count
        self.connect()

    def connect(self):
        self.sdl_joystick = connect_virtual_joystick(
            self.name, self.axis_count, self.ball_count, self.button_count, self.hat_count
        )

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
                assert {(i.__class__, i.name) for i in controller.axes} == {
                    (ControllerAxis, f"axis {i}") for i in range(self.axis_count)
                }
                assert {(i.__class__, i.name) for i in controller.balls} == {
                    (ControllerBall, f"ball {i}") for i in range(self.ball_count)
                }
                assert {(i.__class__, i.name) for i in controller.buttons} == {
                    (ControllerButton, f"button {i}") for i in range(self.button_count)
                }
                assert {(i.__class__, i.name) for i in controller.hats} == {
                    (ControllerHat, f"hat {i}") for i in range(self.hat_count)
                }
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

        event = capture_event(
            vc.disconnect, getattr(event_object or controller1, disconnected_event_name)
        )
        assert event == {"controller": controller1, "is_connected": False}
        assert not controller1.is_connected
        assert not set(get_controllers())

        event = capture_event(vc.connect, getattr(Controller, connected_event_name))
        controller2 = vc.get_controller()
        assert controller1 is not controller2
        assert event == {"controller": controller2, "is_connected": True}
        assert not controller1.is_connected
        assert controller2.is_connected
        assert set(get_controllers()) == {controller2}


@pytest.mark.parametrize(
    "controller_kwargs",
    [
        {},
        {"name": "Virtual Controller"},
        {"axis_count": 4},
        {"ball_count": 5},
        {"button_count": 6},
        {"hat_count": 7},
    ],
)
def test_properties(capture_event, controller_kwargs):
    vc = VirtualController(**controller_kwargs)
    with Platform():
        vc.get_controller()
        capture_event(vc.disconnect, Controller.disconnected)
        capture_event(vc.connect, Controller.connected)
        vc.get_controller()


@pytest.mark.parametrize("event_object", [ControllerAxis, None])
def test_axis_position(capture_event, event_object):
    vc = VirtualController(axis_count=2)
    with Platform():
        controller = vc.get_controller()
        axis0 = controller.get_axis("axis 0")
        axis1 = controller.get_axis("axis 1")
        assert isclose(axis0.position, 0, abs_tol=1e-04)
        assert isclose(axis1.position, 0, abs_tol=1e-04)

        def _():
            set_virtual_joystick_axis_position(vc.sdl_joystick, 0, -32768)
            assert isclose(axis0.position, 0, abs_tol=1e-04)
            assert isclose(axis1.position, 0, abs_tol=1e-04)

        event = capture_event(_, getattr(event_object or axis0, "changed"))

        assert event == {"axis": axis0, "position": axis0.position}
        assert isclose(axis0.position, -1)
        assert isclose(axis1.position, 0, abs_tol=1e-04)

        def _():
            set_virtual_joystick_axis_position(vc.sdl_joystick, 1, 32767)
            assert isclose(axis0.position, -1)
            assert isclose(axis1.position, 0, abs_tol=1e-04)

        event = capture_event(_, getattr(event_object or axis1, "changed"))
        assert event == {"axis": axis1, "position": axis1.position}
        assert isclose(axis0.position, -1)
        assert isclose(axis1.position, 1)

        def _():
            set_virtual_joystick_axis_position(vc.sdl_joystick, 1, 16384)
            assert isclose(axis0.position, -1)
            assert isclose(axis1.position, 1)

        event = capture_event(_, getattr(event_object or axis1, "changed"))
        assert event == {"axis": axis1, "position": axis1.position}
        assert isclose(axis0.position, -1)
        assert isclose(axis1.position, 0.5, abs_tol=1e-04)
