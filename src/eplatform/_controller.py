__all__ = ["Controller", "discover_controllers", "forget_controllers", "controller_change_axis"]

from typing import ClassVar
from typing import Collection
from typing import Final
from typing import Generator
from typing import Mapping
from typing import NamedTuple
from typing import TypedDict
from uuid import UUID

from eevent import Event

from . import _eplatform
from ._eplatform import SDL_GAMEPAD_BINDTYPE_AXIS
from ._eplatform import SDL_GAMEPAD_BINDTYPE_BUTTON
from ._eplatform import SDL_GAMEPAD_BINDTYPE_HAT
from ._eplatform import close_sdl_joystick
from ._eplatform import get_sdl_joysticks
from ._eplatform import open_sdl_joystick
from ._type import SdlGamepadAxis
from ._type import SdlGamepadButton
from ._type import SdlGamepadButtonLabel
from ._type import SdlJoystickId

_AXIS_MIN: Final = -32768
_AXIS_MAX: Final = 32767


def _normalize_sdl_axis_value(value: int) -> float:
    return min(max(-1.0, ((value - _AXIS_MIN) / (_AXIS_MAX - _AXIS_MIN) * 2) - 1), 1.0)


class ControllerDisconnectedError(RuntimeError):
    pass


"""
class _ControllerAnalogInputAxisMapping(NamedTuple):
    from_min: int
    from_max: int
    to_name: str

    def calculate_to_value(self, from_value: int) -> float:
        from_value = min(max(self.from_min, from_value), self.from_max)
        to_value = (from_value - self.from_min) / (self.from_max - self.from_min)
        to_value = (to_value * 2) - 1.0
        to_value = min(max(-1.0, to_value), 1.0)
        return to_value

    def __call__(self, controller: "Controller", from_value: int) -> bool:
        to_axis = controller.get_axis(self.to_name)
        return to_axis._set_position(self.calculate_to_value(from_value))


class _ControllerButtonButtonMapping(NamedTuple):
    to_name: str

    def __call__(self, controller: "Controller", value: bool) -> bool:
        to_button = controller.get_button(self.to_name)
        return to_button._set_is_pressed(value)





class _ControllerBallMapping(NamedTuple):
    ball_index: int


class _ControllerHatMapping(NamedTuple):
    hat_index: int
    mask: int
"""


class _ControllerInput:
    _controller: "Controller | None"

    def __init__(self, name: str):
        self._controller = None
        self._name = name

    def __repr__(self) -> str:
        if self._controller is None:
            return f"<{self.__class__.__name__}>"
        return f"<{self.__class__.__name__} {self._name!r}>"

    @property
    def is_connected(self):
        return self._controller is not None

    @property
    def controller(self) -> "Controller":
        if self._controller is None:
            raise ControllerDisconnectedError()
        return self._controller

    @property
    def name(self) -> str:
        if self._controller is None:
            raise ControllerDisconnectedError()
        return self._name


class ControllerAnalogInputChanged(TypedDict):
    analog_input: "ControllerAnalogInput"
    value: float


class ControllerAnalogInput(_ControllerInput):
    _value: float

    changed: Event[ControllerAnalogInputChanged] = Event()

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.changed = Event()

    @property
    def value(self) -> float:
        if not self.is_connected:
            raise ControllerDisconnectedError()
        return self._value

    def _set_value(self, value: float) -> bool:
        if self._value == value:
            return False

        self._value = value

        data: ControllerAnalogInputChanged = {"analog_input": self, "value": value}
        ControllerAnalogInput.changed(data)
        self.changed(data)

        return True


class ControllerBinaryInputChanged(TypedDict):
    binary_input: "ControllerBinaryInput"
    value: bool


class ControllerBinaryInput(_ControllerInput):
    _value: bool

    changed: Event[ControllerBinaryInputChanged] = Event()

    def __init__(self, name: str) -> None:
        super().__init__(name)
        self.changed = Event()

    @property
    def value(self) -> bool:
        if not self.is_connected:
            raise ControllerDisconnectedError()
        return self._value

    def _set_value(self, value: bool) -> bool:
        if self._value == value:
            return False

        self._value = value

        data: ControllerBinaryInputChanged = {"binary_input": self, "value": value}
        ControllerBinaryInput.changed(data)
        self.changed(data)

        return True


class ControllerDirectionalInput(_ControllerInput):
    pass


class ControllerConnectionChanged(TypedDict):
    controller: "Controller"
    is_connected: bool


class Controller:
    _sdl_joystick: SdlJoystickId | None = None
    _name: str = ""
    _uuid: UUID = UUID(bytes=b"\x00" * 16)
    _serial: str = ""
    _player_index: int | None = None

    _inputs: dict[
        str, ControllerAnalogInput | ControllerBinaryInput | ControllerDirectionalInput
    ] = {}
    _analog_inputs: tuple[ControllerAnalogInput, ...] = ()
    _binary_inputs: tuple[ControllerBinaryInput, ...] = ()
    _directional_inputs: tuple[ControllerDirectionalInput, ...] = ()

    connection_changed: Event[ControllerConnectionChanged] = Event()
    connected: ClassVar[Event[ControllerConnectionChanged]] = Event()
    disconnected: Event[ControllerConnectionChanged] = Event()

    def __init__(self) -> None:
        self.connection_changed = Event()
        self.disconnected = Event()

    def __repr__(self) -> str:
        if self._sdl_joystick is None:
            return "<Controller>"
        id = self._uuid.hex
        if self._serial:
            id = f"{id} {self._serial}"
        if self._player_index is not None:
            id = f"(Player {self._player_index}) {id}"
        return f"<Controller {self._name!r} {id}>"

    def get_input(
        self, name: str
    ) -> ControllerAnalogInput | ControllerBinaryInput | ControllerDirectionalInput:
        if not self.is_connected:
            raise ControllerDisconnectedError()
        return self._inputs[name]

    def get_analog_input(self, name: str) -> ControllerAnalogInput:
        input = self.get_input(name)
        if not isinstance(input, ControllerAnalogInput):
            raise KeyError(name)
        return input

    def get_binary_input(self, name: str) -> ControllerBinaryInput:
        input = self.get_input(name)
        if not isinstance(input, ControllerBinaryInput):
            raise KeyError(name)
        return input

    def get_directional_input(self, name: str) -> ControllerDirectionalInput:
        input = self.get_input(name)
        if not isinstance(input, ControllerDirectionalInput):
            raise KeyError(name)
        return input

    @property
    def analog_inputs(self) -> Collection[ControllerAnalogInput]:
        if not self.is_connected:
            raise ControllerDisconnectedError()
        return self._analog_inputs

    @property
    def binary_inputs(self) -> Collection[ControllerBinaryInput]:
        if not self.is_connected:
            raise ControllerDisconnectedError()
        return self._binary_inputs

    @property
    def directional_inputs(self) -> Collection[ControllerDirectionalInput]:
        if not self.is_connected:
            raise ControllerDisconnectedError()
        return self._directional_inputs

    @property
    def is_connected(self) -> bool:
        return self._sdl_joystick is not None

    @property
    def name(self) -> str:
        if not self.is_connected:
            raise ControllerDisconnectedError()
        return self._name


_SDL_GAMEPAD_BUTTON_NAME: Final[Mapping[SdlGamepadButton, str]] = {
    _eplatform.SDL_GAMEPAD_BUTTON_SOUTH: "south",
    _eplatform.SDL_GAMEPAD_BUTTON_EAST: "east",
    _eplatform.SDL_GAMEPAD_BUTTON_WEST: "west",
    _eplatform.SDL_GAMEPAD_BUTTON_NORTH: "north",
    _eplatform.SDL_GAMEPAD_BUTTON_BACK: "back",
    _eplatform.SDL_GAMEPAD_BUTTON_GUIDE: "guide",
    _eplatform.SDL_GAMEPAD_BUTTON_START: "start",
    _eplatform.SDL_GAMEPAD_BUTTON_LEFT_STICK: "left stick",
    _eplatform.SDL_GAMEPAD_BUTTON_RIGHT_STICK: "right stick",
    _eplatform.SDL_GAMEPAD_BUTTON_LEFT_SHOULDER: "left shoulder",
    _eplatform.SDL_GAMEPAD_BUTTON_RIGHT_SHOULDER: "right shoulder",
    _eplatform.SDL_GAMEPAD_BUTTON_DPAD_UP: "dpad up",
    _eplatform.SDL_GAMEPAD_BUTTON_DPAD_DOWN: "dpad down",
    _eplatform.SDL_GAMEPAD_BUTTON_DPAD_LEFT: "dpad left",
    _eplatform.SDL_GAMEPAD_BUTTON_DPAD_RIGHT: "dpad right",
    _eplatform.SDL_GAMEPAD_BUTTON_MISC1: "button 1",
    _eplatform.SDL_GAMEPAD_BUTTON_RIGHT_PADDLE1: "right paddle",
    _eplatform.SDL_GAMEPAD_BUTTON_LEFT_PADDLE1: "left paddle",
    _eplatform.SDL_GAMEPAD_BUTTON_RIGHT_PADDLE2: "right paddle 2",
    _eplatform.SDL_GAMEPAD_BUTTON_LEFT_PADDLE2: "left paddle 2",
    _eplatform.SDL_GAMEPAD_BUTTON_TOUCHPAD: "touchpad",
    _eplatform.SDL_GAMEPAD_BUTTON_MISC2: "button 2",
    _eplatform.SDL_GAMEPAD_BUTTON_MISC3: "button 3",
    _eplatform.SDL_GAMEPAD_BUTTON_MISC4: "button 4",
    _eplatform.SDL_GAMEPAD_BUTTON_MISC5: "button 5",
    _eplatform.SDL_GAMEPAD_BUTTON_MISC6: "button 6",
}

_SDL_GAMEPAD_BUTTON_LABEL_NAME: Final[Mapping[SdlGamepadButtonLabel, str]] = {
    _eplatform.SDL_GAMEPAD_BUTTON_LABEL_A: "a",
    _eplatform.SDL_GAMEPAD_BUTTON_LABEL_B: "b",
    _eplatform.SDL_GAMEPAD_BUTTON_LABEL_X: "x",
    _eplatform.SDL_GAMEPAD_BUTTON_LABEL_Y: "y",
    _eplatform.SDL_GAMEPAD_BUTTON_LABEL_CROSS: "cross",
    _eplatform.SDL_GAMEPAD_BUTTON_LABEL_CIRCLE: "circle",
    _eplatform.SDL_GAMEPAD_BUTTON_LABEL_SQUARE: "square",
    _eplatform.SDL_GAMEPAD_BUTTON_LABEL_TRIANGLE: "triangle",
}

_SDL_GAMEPAD_AXIS_NAME: Final[Mapping[SdlGamepadAxis, str]] = {
    _eplatform.SDL_GAMEPAD_AXIS_LEFTX: "left x",
    _eplatform.SDL_GAMEPAD_AXIS_LEFTY: "left y",
    _eplatform.SDL_GAMEPAD_AXIS_RIGHTX: "right x",
    _eplatform.SDL_GAMEPAD_AXIS_RIGHTY: "right y",
    _eplatform.SDL_GAMEPAD_AXIS_LEFT_TRIGGER: "left trigger",
    _eplatform.SDL_GAMEPAD_AXIS_RIGHT_TRIGGER: "right trigger",
}

# we shouldn't be generating inputs with the same name
assert (
    len(_SDL_GAMEPAD_BUTTON_NAME)
    + len(_SDL_GAMEPAD_BUTTON_LABEL_NAME)
    + len(_SDL_GAMEPAD_AXIS_NAME)
) == len(
    set(
        (
            *_SDL_GAMEPAD_BUTTON_NAME.values(),
            *_SDL_GAMEPAD_BUTTON_LABEL_NAME.values(),
            *_SDL_GAMEPAD_AXIS_NAME.values(),
        )
    )
)

_controllers: dict[SdlJoystickId, Controller] = {}


def get_controllers() -> Generator[Controller, None, None]:
    yield from _controllers.values()


def connect_controller(sdl_joystick: SdlJoystickId) -> None:
    assert sdl_joystick not in _controllers
    _controllers[sdl_joystick] = controller = Controller()

    (
        name,
        guid,
        serial,
        player_index,
        ball_count,
        hat_count,
        axis_details,
        button_details,
        mapping_details,
    ) = open_sdl_joystick(sdl_joystick)
    controller._sdl_joystick = sdl_joystick
    controller._name = name
    controller._uuid = UUID(hex=guid)
    controller._serial = serial or ""
    controller._player_index = player_index if player_index >= 0 else None

    analog_inputs: list[ControllerAnalogInput] = []
    binary_inputs: list[ControllerBinaryInput] = []
    directional_inputs: list[ControllerDirectionalInput] = []

    if mapping_details is None:
        for i, (value,) in enumerate(axis_details):
            name = f"analog {i}"
            input = ControllerAnalogInput(name)
            input._controller = controller
            input._value = _normalize_sdl_axis_value(value)
            analog_inputs.append(input)

        for i, (value,) in enumerate(button_details):
            name = f"binary {i}"
            input = ControllerBinaryInput(name)
            input._controller = controller
            input._value = value
            binary_inputs.append(input)

        for i in range(hat_count):
            name = f"directional {i}"
            input = ControllerDirectionalInput(name)
            input._controller = controller
            # input._value = 0
            directional_inputs.append(input)

    else:
        raise RuntimeError("nope")
        """
        for (input_type, *input_args), (output_type, *output_args) in mapping_details:
            if input_type == SDL_GAMEPAD_BINDTYPE_BUTTON:
                mapping = _ControllerButtonMapping(*input_args)
            elif input_type == SDL_GAMEPAD_BINDTYPE_AXIS:
                mapping = _ControllerAnalogInputMapping(*input_args)
            elif input_type == SDL_GAMEPAD_BINDTYPE_HAT:
                mapping = _ControllerHatMapping(*input_args)
            else:
                raise RuntimeError(f"unexpected input type {input_type!r}")

            if output_type == SDL_GAMEPAD_BINDTYPE_BUTTON:
                button, button_label = output_args
                try:
                    name = _SDL_GAMEPAD_BUTTON_LABEL_NAME[button_label]
                except KeyError:
                    name = _SDL_GAMEPAD_BUTTON_NAME[button]
                button = ControllerButton(name)
                if not isinstance(mapping, (_ControllerButtonMapping, _ControllerHatMapping)):
                    raise RuntimeError(f"unexpected mapping for button output: {mapping!r}")
                button._mapping = mapping
                buttons.append(button)
            elif output_type == SDL_GAMEPAD_BINDTYPE_AXIS:
                axis, axis_min, axis_max = output_args
                name = _SDL_GAMEPAD_AXIS_NAME[axis]
                axis = ControllerAnalogInput(name)
                axis._min = axis_min
                axis._max = axis_max
                if not isinstance(mapping, _ControllerAnalogInputMapping):
                    raise RuntimeError(f"unexpected mapping for axis output: {mapping!r}")
                axis._mapping = mapping
                axes.append(axis)
            else:
                raise RuntimeError(f"unexpected output type {output_type!r}")
        """

    controller._inputs = {i.name: i for i in (*analog_inputs, *binary_inputs, *directional_inputs)}
    if len(controller._inputs) != (
        len(analog_inputs) + len(binary_inputs) + len(directional_inputs)
    ):
        raise RuntimeError("controller inputs have the same name")
    controller._analog_inputs = tuple(analog_inputs)
    controller._binary_inputs = tuple(binary_inputs)
    controller._directional_inputs = tuple(directional_inputs)

    data: ControllerConnectionChanged = {"controller": controller, "is_connected": True}
    Controller.connection_changed(data)
    Controller.connected(data)


def disconnect_controller(sdl_joystick: SdlJoystickId) -> None:
    controller = _controllers.pop(sdl_joystick)
    controller._sdl_joystick = None
    for input in controller._inputs.values():
        input._controller = None

    close_sdl_joystick(sdl_joystick)

    data: ControllerConnectionChanged = {"controller": controller, "is_connected": False}
    Controller.connection_changed(data)
    controller.connection_changed(data)
    Controller.disconnected(data)
    controller.disconnected(data)


def discover_controllers() -> None:
    for sdl_joystick in get_sdl_joysticks():
        connect_controller(sdl_joystick)


def forget_controllers() -> None:
    for sdl_joystick in list(_controllers.keys()):
        disconnect_controller(sdl_joystick)


def controller_change_axis(sdl_joystick: SdlJoystickId, axis_index: int, value: int) -> bool:
    controller = _controllers[sdl_joystick]
    input = controller._analog_inputs[axis_index]
    return input._set_value(_normalize_sdl_axis_value(value))


def controller_change_button(
    sdl_joystick: SdlJoystickId, button_index: int, is_pressed: bool
) -> bool:
    controller = _controllers[sdl_joystick]
    input = controller._binary_inputs[button_index]
    return input._set_value(is_pressed)
