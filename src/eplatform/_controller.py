__all__ = ["Controller", "discover_controllers", "forget_controllers"]

from typing import Collection
from typing import Final
from typing import Generator
from typing import Mapping
from typing import NamedTuple
from uuid import UUID

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


class _ControllerAxisMapping(NamedTuple):
    axis_index: int
    min: int
    max: int


class _ControllerButtonMapping(NamedTuple):
    button_index: int


class _ControllerBallMapping(NamedTuple):
    ball_index: int


class _ControllerHatMapping(NamedTuple):
    hat_index: int
    mask: int


class _ControllerInput:
    def __init__(self, name: str):
        self._name = name

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self.name!r}>"

    @property
    def name(self) -> str:
        return self._name


class ControllerAxis(_ControllerInput):
    _min: int = _AXIS_MIN
    _max: int = _AXIS_MAX
    _mapping: _ControllerAxisMapping


class ControllerButton(_ControllerInput):
    _mapping: _ControllerButtonMapping | _ControllerHatMapping


class ControllerBall(_ControllerInput):
    _mapping: _ControllerBallMapping


class ControllerHat(_ControllerInput):
    _mapping: _ControllerHatMapping


class Controller:
    _sdl_joystick: SdlJoystickId | None = None
    _name: str = ""
    _uuid: UUID = UUID(bytes=b"\x00" * 16)
    _serial: str = ""
    _player_index: int | None = None

    _axes: dict[str, ControllerAxis] = {}
    _balls: dict[str, ControllerBall] = {}
    _buttons: dict[str, ControllerButton] = {}
    _hats: dict[str, ControllerHat] = {}

    def get_input(
        self, name: str
    ) -> ControllerAxis | ControllerBall | ControllerButton | ControllerHat:
        try:
            return self._buttons[name]
        except KeyError:
            pass
        try:
            return self._axes[name]
        except KeyError:
            pass
        try:
            return self._hats[name]
        except KeyError:
            pass
        return self._balls[name]

    def get_axis(self, name: str) -> ControllerAxis:
        return self._axes[name]

    def get_ball(self, name: str) -> ControllerBall:
        return self._balls[name]

    def get_button(self, name: str) -> ControllerButton:
        return self._buttons[name]

    def get_hat(self, name: str) -> ControllerHat:
        return self._hats[name]

    @property
    def axes(self) -> Collection[ControllerAxis]:
        return self._axes.values()

    @property
    def balls(self) -> Collection[ControllerBall]:
        return self._balls.values()

    @property
    def buttons(self) -> Collection[ControllerButton]:
        return self._buttons.values()

    @property
    def hats(self) -> Collection[ControllerHat]:
        return self._hats.values()

    def __repr__(self) -> str:
        if self._sdl_joystick is None:
            return "<Controller>"
        id = self._uuid.hex
        if self._serial:
            id = f"{id} {self._serial}"
        if self._player_index is not None:
            id = f"(Player {self._player_index}) {id}"
        return f"<Controller {self._name!r} {id}>"


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
        axis_count,
        ball_count,
        button_count,
        hat_count,
        mapping_details,
    ) = open_sdl_joystick(sdl_joystick)
    controller._sdl_joystick = sdl_joystick
    controller._name = name
    controller._uuid = UUID(hex=guid)
    controller._serial = serial or ""
    controller._player_index = player_index if player_index >= 0 else None

    axes: list[ControllerAxis] = []
    balls: list[ControllerBall] = []
    buttons: list[ControllerButton] = []
    hats: list[ControllerHat] = []
    if mapping_details is None:
        for i in range(axis_count):
            axis = ControllerAxis(f"axis {i}")
            axis._mapping = _ControllerAxisMapping(i, _AXIS_MIN, _AXIS_MAX)
            axes.append(axis)

        for i in range(ball_count):
            ball = ControllerBall(f"ball {i}")
            ball._mapping = _ControllerBallMapping(i)
            balls.append(ball)

        for i in range(button_count):
            button = ControllerButton(f"button {i}")
            button._mapping = _ControllerButtonMapping(i)
            buttons.append(button)

        for i in range(hat_count):
            hat = ControllerHat(f"hat {i}")
            hat._mapping = _ControllerHatMapping(i, 0)
            hats.append(hat)

    else:
        for (input_type, *input_args), (output_type, *output_args) in mapping_details:
            if input_type == SDL_GAMEPAD_BINDTYPE_BUTTON:
                mapping = _ControllerButtonMapping(*input_args)
            elif input_type == SDL_GAMEPAD_BINDTYPE_AXIS:
                mapping = _ControllerAxisMapping(*input_args)
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
                axis = ControllerAxis(name)
                axis._min = axis_min
                axis._max = axis_max
                if not isinstance(mapping, _ControllerAxisMapping):
                    raise RuntimeError(f"unexpected mapping for axis output: {mapping!r}")
                axis._mapping = mapping
                axes.append(axis)
            else:
                raise RuntimeError(f"unexpected output type {output_type!r}")

    controller._axes = {i.name: i for i in axes}
    controller._balls = {i.name: i for i in balls}
    controller._buttons = {i.name: i for i in buttons}
    controller._hats = {i.name: i for i in hats}
    # we shouldn't be generating inputs with the same name
    assert len(controller._axes) == len(axes)
    assert len(controller._balls) == len(balls)
    assert len(controller._buttons) == len(buttons)
    assert len(controller._hats) == len(hats)
    assert (
        len(controller._axes)
        + len(controller._balls)
        + len(controller._buttons)
        + len(controller._hats)
    ) == (len(axes) + len(balls) + len(buttons) + len(hats))


def disconnect_controller(sdl_joystick: SdlJoystickId) -> None:
    close_sdl_joystick(sdl_joystick)


def discover_controllers() -> None:
    for sdl_joystick in get_sdl_joysticks():
        connect_controller(sdl_joystick)


def forget_controllers() -> None:
    for sdl_joystick in list(_controllers.keys()):
        disconnect_controller(sdl_joystick)
