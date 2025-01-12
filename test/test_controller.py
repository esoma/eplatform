from math import isclose
from unittest.mock import ANY
from uuid import uuid4

import pytest

from eplatform import Controller
from eplatform import ControllerAnalogInput
from eplatform import ControllerBinaryInput
from eplatform import ControllerDirectionalInput
from eplatform import Platform
from eplatform import get_controllers
from eplatform._eplatform import connect_virtual_joystick
from eplatform._eplatform import disconnect_virtual_joystick
from eplatform._eplatform import set_virtual_joystick_axis_position
from eplatform._eplatform import set_virtual_joystick_button_press


class VirtualController:
    def __init__(self, *, name=None, axis_count=0, button_count=0, hat_count=0):
        self.sdl_joystick = None
        self.name = name or uuid4().hex
        self.axis_count = axis_count
        self.button_count = button_count
        self.hat_count = hat_count
        self.connect()

    def connect(self):
        self.sdl_joystick = connect_virtual_joystick(
            self.name, self.axis_count, 0, self.button_count, self.hat_count
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
                assert {(i.__class__, i.name) for i in controller.analog_inputs} == {
                    (ControllerAnalogInput, f"analog {i}") for i in range(self.axis_count)
                }
                assert {(i.__class__, i.name) for i in controller.binary_inputs} == {
                    (ControllerBinaryInput, f"binary {i}") for i in range(self.button_count)
                }
                assert {(i.__class__, i.name) for i in controller.directional_inputs} == {
                    (ControllerDirectionalInput, f"directional {i}") for i in range(self.hat_count)
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
    [{}, {"name": "Virtual Controller"}, {"axis_count": 4}, {"button_count": 6}, {"hat_count": 7}],
)
def test_properties(capture_event, controller_kwargs):
    vc = VirtualController(**controller_kwargs)
    with Platform():
        vc.get_controller()
        capture_event(vc.disconnect, Controller.disconnected)
        capture_event(vc.connect, Controller.connected)
        vc.get_controller()


@pytest.mark.parametrize("event_object", [ControllerAnalogInput, None])
def test_analog_value(capture_event, event_object):
    vc = VirtualController(axis_count=2)
    with Platform():
        controller = vc.get_controller()
        analog0 = controller.get_analog_input("analog 0")
        analog1 = controller.get_analog_input("analog 1")
        assert isclose(analog0.value, 0, abs_tol=1e-04)
        assert isclose(analog1.value, 0, abs_tol=1e-04)

        def _():
            set_virtual_joystick_axis_position(vc.sdl_joystick, 0, -32768)
            assert isclose(analog0.value, 0, abs_tol=1e-04)
            assert isclose(analog1.value, 0, abs_tol=1e-04)

        event = capture_event(_, getattr(event_object or analog0, "changed"))

        assert event == {"analog_input": analog0, "value": analog0.value}
        assert isclose(analog0.value, -1)
        assert isclose(analog1.value, 0, abs_tol=1e-04)

        def _():
            set_virtual_joystick_axis_position(vc.sdl_joystick, 1, 32767)
            assert isclose(analog0.value, -1)
            assert isclose(analog1.value, 0, abs_tol=1e-04)

        event = capture_event(_, getattr(event_object or analog1, "changed"))
        assert event == {"analog_input": analog1, "value": analog1.value}
        assert isclose(analog0.value, -1)
        assert isclose(analog1.value, 1)

        def _():
            set_virtual_joystick_axis_position(vc.sdl_joystick, 1, 16384)
            assert isclose(analog0.value, -1)
            assert isclose(analog1.value, 1)

        event = capture_event(_, getattr(event_object or analog1, "changed"))
        assert event == {"analog_input": analog1, "value": analog1.value}
        assert isclose(analog0.value, -1)
        assert isclose(analog1.value, 0.5, abs_tol=1e-04)


@pytest.mark.parametrize("event_object", [ControllerBinaryInput, None])
def test_binary_value(capture_event, event_object):
    vc = VirtualController(button_count=2)
    with Platform():
        controller = vc.get_controller()
        binary0 = controller.get_binary_input("binary 0")
        binary1 = controller.get_binary_input("binary 1")
        assert not binary0.value
        assert not binary1.value

        def _():
            set_virtual_joystick_button_press(vc.sdl_joystick, 0, True)
            assert not binary0.value
            assert not binary1.value

        event = capture_event(_, getattr(event_object or binary0, "changed"))

        assert event == {"binary_input": binary0, "value": True}
        assert binary0.value
        assert not binary1.value

        def _():
            set_virtual_joystick_button_press(vc.sdl_joystick, 1, True)
            assert binary0.value
            assert not binary1.value

        event = capture_event(_, getattr(event_object or binary1, "changed"))

        assert event == {"binary_input": binary1, "value": True}
        assert binary0.value
        assert binary1.value

        def _():
            set_virtual_joystick_button_press(vc.sdl_joystick, 1, False)
            assert binary0.value
            assert binary1.value

        event = capture_event(_, getattr(event_object or binary1, "changed"))

        assert event == {"binary_input": binary1, "value": False}
        assert binary0.value
        assert not binary1.value
