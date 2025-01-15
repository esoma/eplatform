from math import isclose
from unittest.mock import ANY
from uuid import uuid4

import pytest
from emath import DVector2

from eplatform import Controller
from eplatform import ControllerAnalogInput
from eplatform import ControllerBinaryInput
from eplatform import ControllerButton
from eplatform import ControllerButtonName
from eplatform import ControllerDirectionalInput
from eplatform import ControllerDirectionalInputValue
from eplatform import ControllerStick
from eplatform import ControllerStickName
from eplatform import ControllerTrigger
from eplatform import ControllerTriggerName
from eplatform import Platform
from eplatform import get_controllers
from eplatform._eplatform import SDL_HAT_DOWN
from eplatform._eplatform import SDL_HAT_LEFT
from eplatform._eplatform import SDL_HAT_RIGHT
from eplatform._eplatform import SDL_HAT_UP
from eplatform._eplatform import add_sdl_gamepad_mapping
from eplatform._eplatform import connect_virtual_joystick
from eplatform._eplatform import disconnect_virtual_joystick
from eplatform._eplatform import set_virtual_joystick_axis_position
from eplatform._eplatform import set_virtual_joystick_button_press
from eplatform._eplatform import set_virtual_joystick_hat_value

GAMEPAD_MAP_TO_BUTTON_NAME = {
    "a": ControllerButtonName.A,
    "b": ControllerButtonName.B,
    "x": ControllerButtonName.X,
    "y": ControllerButtonName.Y,
    "back": ControllerButtonName.BACK,
    "guide": ControllerButtonName.GUIDE,
    "start": ControllerButtonName.START,
    "leftstick": ControllerButtonName.LEFT_STICK,
    "rightstick": ControllerButtonName.RIGHT_STICK,
    "leftshoulder": ControllerButtonName.LEFT_SHOULDER,
    "rightshoulder": ControllerButtonName.RIGHT_SHOULDER,
    "dpup": ControllerButtonName.UP,
    "dpdown": ControllerButtonName.DOWN,
    "dpleft": ControllerButtonName.LEFT,
    "dpright": ControllerButtonName.RIGHT,
    "paddle1": ControllerButtonName.RIGHT_PADDLE_1,
    "paddle2": ControllerButtonName.LEFT_PADDLE_1,
    "paddle3": ControllerButtonName.RIGHT_PADDLE_2,
    "paddle4": ControllerButtonName.LEFT_PADDLE_2,
    "touchpad": ControllerButtonName.TOUCHPAD,
}

GAMEPAD_MAP_TO_STICK_NAME = {
    "leftx": ControllerStickName.LEFT,
    "lefty": ControllerStickName.LEFT,
    "rightx": ControllerStickName.RIGHT,
    "righty": ControllerStickName.RIGHT,
}

GAMEPAD_MAP_TO_TRIGGER_NAME = {
    "lefttrigger": ControllerTriggerName.LEFT,
    "righttrigger": ControllerTriggerName.RIGHT,
}


class VirtualController:
    def __init__(
        self,
        *,
        name="Test",
        expected_uuid_hex="ff002538546573740000000000007600",
        axis_count=0,
        button_count=0,
        hat_count=0,
        gamepad_name=None,
        gamepad_map={},
    ):
        self.expected_uuid_hex = expected_uuid_hex
        if gamepad_name is None:
            gamepad_name = name
        self.gamepad_map = gamepad_map
        gamepad_map_inputs = ",".join(f"{k}:{v}" for k, v in gamepad_map.items())
        add_sdl_gamepad_mapping(f"{expected_uuid_hex},{gamepad_name},{gamepad_map_inputs}")
        self.sdl_joystick = None
        self.name = name
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
                assert controller.uuid.hex == self.expected_uuid_hex
                assert {(i.__class__, i.name) for i in controller.analog_inputs} == {
                    (ControllerAnalogInput, f"analog {i}") for i in range(self.axis_count)
                }
                assert {(i.__class__, i.name) for i in controller.binary_inputs} == {
                    (ControllerBinaryInput, f"binary {i}") for i in range(self.button_count)
                }
                assert {(i.__class__, i.name) for i in controller.directional_inputs} == {
                    (ControllerDirectionalInput, f"directional {i}") for i in range(self.hat_count)
                }
                assert {(i.__class__, i.name) for i in controller.buttons} == {
                    (ControllerButton, GAMEPAD_MAP_TO_BUTTON_NAME[n.lstrip("-+")])
                    for n in self.gamepad_map.keys()
                    if n.lstrip("-+") in GAMEPAD_MAP_TO_BUTTON_NAME
                }
                assert {(i.__class__, i.name) for i in controller.sticks} == {
                    (ControllerStick, GAMEPAD_MAP_TO_STICK_NAME[n.lstrip("-+")])
                    for n in self.gamepad_map.keys()
                    if n.lstrip("-+") in GAMEPAD_MAP_TO_STICK_NAME
                }
                assert {(i.__class__, i.name) for i in controller.triggers} == {
                    (ControllerTrigger, GAMEPAD_MAP_TO_TRIGGER_NAME[n.lstrip("-+")])
                    for n in self.gamepad_map.keys()
                    if n.lstrip("-+") in GAMEPAD_MAP_TO_TRIGGER_NAME
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
        {"name": "Virtual Controller", "expected_uuid_hex": "ff0013db5669727475616c2043007600"},
        {"axis_count": 4, "gamepad_map": {"leftx": "a0", "lefty": "a1", "lefttrigger": "a2"}},
        {"button_count": 6, "gamepad_map": {"a": "b0"}},
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
            set_virtual_joystick_axis_position(vc.sdl_joystick, 0, -1.0)
            assert isclose(analog0.value, 0, abs_tol=1e-04)
            assert isclose(analog1.value, 0, abs_tol=1e-04)

        event = capture_event(_, getattr(event_object or analog0, "changed"))

        assert event == {"analog_input": analog0, "value": analog0.value}
        assert isclose(analog0.value, -1)
        assert isclose(analog1.value, 0, abs_tol=1e-04)

        def _():
            set_virtual_joystick_axis_position(vc.sdl_joystick, 1, 1.0)
            assert isclose(analog0.value, -1)
            assert isclose(analog1.value, 0, abs_tol=1e-04)

        event = capture_event(_, getattr(event_object or analog1, "changed"))
        assert event == {"analog_input": analog1, "value": analog1.value}
        assert isclose(analog0.value, -1)
        assert isclose(analog1.value, 1)

        def _():
            set_virtual_joystick_axis_position(vc.sdl_joystick, 1, 0.5)
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


@pytest.mark.parametrize("event_object", [ControllerDirectionalInput, None])
def test_directional_value(capture_event, event_object):
    vc = VirtualController(hat_count=2)
    with Platform():
        controller = vc.get_controller()
        directional0 = controller.get_directional_input("directional 0")
        directional1 = controller.get_directional_input("directional 1")
        assert directional0.value == ControllerDirectionalInputValue.NEUTRAL
        assert directional1.value == ControllerDirectionalInputValue.NEUTRAL

        def _():
            set_virtual_joystick_hat_value(
                vc.sdl_joystick, 0, ControllerDirectionalInputValue.LEFT
            )
            assert directional0.value == ControllerDirectionalInputValue.NEUTRAL
            assert directional1.value == ControllerDirectionalInputValue.NEUTRAL

        event = capture_event(_, getattr(event_object or directional0, "changed"))

        assert event == {"directional_input": directional0, "value": directional0.value}
        assert directional0.value == ControllerDirectionalInputValue.LEFT
        assert directional1.value == ControllerDirectionalInputValue.NEUTRAL

        def _():
            set_virtual_joystick_hat_value(
                vc.sdl_joystick, 1, ControllerDirectionalInputValue.UP_RIGHT
            )
            assert directional0.value == ControllerDirectionalInputValue.LEFT
            assert directional1.value == ControllerDirectionalInputValue.NEUTRAL

        event = capture_event(_, getattr(event_object or directional1, "changed"))

        assert event == {"directional_input": directional1, "value": directional1.value}
        assert directional0.value == ControllerDirectionalInputValue.LEFT
        assert directional1.value == ControllerDirectionalInputValue.UP_RIGHT

        def _():
            set_virtual_joystick_hat_value(vc.sdl_joystick, 1, ControllerDirectionalInputValue.ALL)
            assert directional0.value == ControllerDirectionalInputValue.LEFT
            assert directional1.value == ControllerDirectionalInputValue.UP_RIGHT

        event = capture_event(_, getattr(event_object or directional1, "changed"))

        assert event == {"directional_input": directional1, "value": directional1.value}
        assert directional0.value == ControllerDirectionalInputValue.LEFT
        assert directional1.value == ControllerDirectionalInputValue.ALL


@pytest.mark.parametrize("event_object", [ControllerButton, None])
@pytest.mark.parametrize("mapped_binary_index", [0, 1])
@pytest.mark.parametrize("mapped_button, button_name", GAMEPAD_MAP_TO_BUTTON_NAME.items())
@pytest.mark.parametrize("event_name", ["changed", None])
def test_button_binary_mapped(
    capture_event, event_object, mapped_binary_index, mapped_button, button_name, event_name
):
    vc = VirtualController(button_count=2, gamepad_map={mapped_button: f"b{mapped_binary_index}"})
    with Platform():
        controller = vc.get_controller()
        button = controller.get_button(button_name)

        def _():
            set_virtual_joystick_button_press(vc.sdl_joystick, mapped_binary_index, True)
            assert not button.is_pressed

        event = capture_event(_, getattr(event_object or button, event_name or "pressed"))

        assert event == {"button": button, "is_pressed": True}
        assert button.is_pressed

        def _():
            set_virtual_joystick_button_press(vc.sdl_joystick, mapped_binary_index, False)
            assert button.is_pressed

        event = capture_event(_, getattr(event_object or button, event_name or "released"))

        assert event == {"button": button, "is_pressed": False}
        assert not button.is_pressed


@pytest.mark.parametrize("event_object", [ControllerButton, None])
@pytest.mark.parametrize("mapped_directional_index", [0, 1])
@pytest.mark.parametrize(
    "mapped_mask, directional_value",
    [
        (8, ControllerDirectionalInputValue.LEFT),
        (4, ControllerDirectionalInputValue.DOWN),
        (2, ControllerDirectionalInputValue.RIGHT),
        (1, ControllerDirectionalInputValue.UP),
    ],
)
@pytest.mark.parametrize("mapped_button, button_name", GAMEPAD_MAP_TO_BUTTON_NAME.items())
@pytest.mark.parametrize("event_name", ["changed", None])
def test_button_directional_mapped(
    capture_event,
    event_object,
    mapped_directional_index,
    mapped_mask,
    directional_value,
    mapped_button,
    button_name,
    event_name,
):
    vc = VirtualController(
        hat_count=2, gamepad_map={mapped_button: f"h{mapped_directional_index}.{mapped_mask}"}
    )
    with Platform():
        controller = vc.get_controller()
        button = controller.get_button(button_name)

        def _():
            set_virtual_joystick_hat_value(
                vc.sdl_joystick, mapped_directional_index, directional_value
            )
            assert not button.is_pressed

        event = capture_event(_, getattr(event_object or button, event_name or "pressed"))

        assert event == {"button": button, "is_pressed": True}
        assert button.is_pressed

        def _():
            set_virtual_joystick_hat_value(
                vc.sdl_joystick, mapped_directional_index, ControllerDirectionalInputValue.NEUTRAL
            )
            assert button.is_pressed

        event = capture_event(_, getattr(event_object or button, event_name or "released"))

        assert event == {"button": button, "is_pressed": False}
        assert not button.is_pressed

        def _():
            set_virtual_joystick_hat_value(
                vc.sdl_joystick, mapped_directional_index, ControllerDirectionalInputValue.ALL
            )
            assert not button.is_pressed

        event = capture_event(_, getattr(event_object or button, event_name or "pressed"))

        assert event == {"button": button, "is_pressed": True}
        assert button.is_pressed


@pytest.mark.parametrize("input_inverted, input_c", [("", 1.0), ("~", -1.0)])
@pytest.mark.parametrize(
    "mapped_stick, stick_name", [("left", "left stick"), ("right", "right stick")]
)
@pytest.mark.parametrize("x_mapped_analog_index, y_mapped_analog_index", [(0, 1), (1, 2)])
@pytest.mark.parametrize("event_object", [ControllerStick, None])
def test_stick_analog_mapped(
    capture_event,
    event_object,
    x_mapped_analog_index,
    y_mapped_analog_index,
    mapped_stick,
    stick_name,
    input_inverted,
    input_c,
):
    vc = VirtualController(
        axis_count=3,
        gamepad_map={
            f"{mapped_stick}x": f"a{x_mapped_analog_index}{input_inverted}",
            f"{mapped_stick}y": f"a{y_mapped_analog_index}{input_inverted}",
        },
    )
    with Platform():
        controller = vc.get_controller()
        stick = controller.get_stick(stick_name)

        def _():
            set_virtual_joystick_axis_position(
                vc.sdl_joystick, x_mapped_analog_index, 1.0 * input_c
            )
            assert isclose(stick.vector.x, 0, abs_tol=1e-04)
            assert isclose(stick.vector.y, 0, abs_tol=1e-04)

        event = capture_event(_, getattr(event_object or stick, "changed"))

        assert event == {"stick": stick, "vector": stick.vector}
        assert isclose(stick.vector.x, 1.0, abs_tol=1e-04)
        assert isclose(stick.vector.y, 0, abs_tol=1e-04)

        def _():
            set_virtual_joystick_axis_position(
                vc.sdl_joystick, y_mapped_analog_index, -1.0 * input_c
            )
            assert isclose(stick.vector.x, 1.0, abs_tol=1e-04)
            assert isclose(stick.vector.y, 0, abs_tol=1e-04)

        event = capture_event(_, getattr(event_object or stick, "changed"))
        assert event == {"stick": stick, "vector": stick.vector}
        assert isclose(stick.vector.x, 1.0, abs_tol=1e-04)
        assert isclose(stick.vector.y, -1.0, abs_tol=1e-04)

        def _():
            set_virtual_joystick_axis_position(
                vc.sdl_joystick, y_mapped_analog_index, 0.5 * input_c
            )
            assert isclose(stick.vector.x, 1.0, abs_tol=1e-04)
            assert isclose(stick.vector.y, -1.0, abs_tol=1e-04)

        event = capture_event(_, getattr(event_object or stick, "changed"))
        assert event == {"stick": stick, "vector": stick.vector}
        assert isclose(stick.vector.x, 1.0, abs_tol=1e-04)
        assert isclose(stick.vector.y, 0.5, abs_tol=1e-04)


@pytest.mark.parametrize("input_inverted, input_c", [("", 1.0), ("~", -1.0)])
@pytest.mark.parametrize("mapped_trigger, trigger_name", GAMEPAD_MAP_TO_TRIGGER_NAME.items())
@pytest.mark.parametrize("mapped_analog_index", [0, 1])
@pytest.mark.parametrize("event_object", [ControllerTrigger, None])
def test_trigger_analog_mapped(
    capture_event,
    event_object,
    mapped_analog_index,
    mapped_trigger,
    trigger_name,
    input_inverted,
    input_c,
):
    vc = VirtualController(
        axis_count=2, gamepad_map={f"{mapped_trigger}": f"a{mapped_analog_index}{input_inverted}"}
    )
    with Platform():
        controller = vc.get_controller()
        trigger = controller.get_trigger(trigger_name)

        def _():
            set_virtual_joystick_axis_position(vc.sdl_joystick, mapped_analog_index, 1 * input_c)
            assert isclose(trigger.position, 0, abs_tol=1e-04)

        event = capture_event(_, getattr(event_object or trigger, "changed"))

        assert event == {"trigger": trigger, "position": trigger.position}
        assert isclose(trigger.position, 1, abs_tol=1e-04)

        def _():
            set_virtual_joystick_axis_position(vc.sdl_joystick, mapped_analog_index, -1 * input_c)
            assert isclose(trigger.position, 1, abs_tol=1e-04)

        event = capture_event(_, getattr(event_object or trigger, "changed"))

        assert event == {"trigger": trigger, "position": trigger.position}
        assert isclose(trigger.position, 0, abs_tol=1e-04)

        def _():
            set_virtual_joystick_axis_position(vc.sdl_joystick, mapped_analog_index, 0 * input_c)
            assert isclose(trigger.position, 0, abs_tol=1e-04)

        event = capture_event(_, getattr(event_object or trigger, "changed"))

        assert event == {"trigger": trigger, "position": trigger.position}
        assert isclose(trigger.position, 0.5, abs_tol=1e-04)
