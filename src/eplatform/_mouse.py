from __future__ import annotations

__all__ = [
    "Mouse",
    "MouseButton",
    "MouseButtonChanged",
    "MouseButtonName",
    "MouseMoved",
    "MouseScrolled",
    "MouseScrolledDirection",
]

# eplatform
from ._platform import get_window

# eevent
from eevent import Event

# emath
from emath import IVector2

# python
from typing import Literal
from typing import TypeAlias
from typing import TypedDict

MouseButtonName: TypeAlias = Literal["left", "right", "middle", "forward", "back"]


class MouseButton:
    def __init__(self, name: MouseButtonName):
        self.name = name
        self.is_pressed = False

        self.changed: Event[MouseButtonChanged] = Event()
        self.pressed: Event[MouseButtonChanged] = Event()
        self.released: Event[MouseButtonChanged] = Event()

    def __repr__(self) -> str:
        return f"<MouseButton {self.name!r}>"


class Mouse:
    def __init__(self) -> None:
        self.position = IVector2(0, 0)
        self.moved: Event[MouseMoved] = Event()

        self.scrolled: Event[MouseScrolled] = Event()
        self.scrolled_vertically: Event[MouseScrolledDirection] = Event()
        self.scrolled_up: Event[MouseScrolledDirection] = Event()
        self.scrolled_down: Event[MouseScrolledDirection] = Event()
        self.scrolled_horizontally: Event[MouseScrolledDirection] = Event()
        self.scrolled_left: Event[MouseScrolledDirection] = Event()
        self.scrolled_right: Event[MouseScrolledDirection] = Event()

        self.left = MouseButton("left")
        self.right = MouseButton("right")
        self.middle = MouseButton("middle")
        self.forward = MouseButton("forward")
        self.back = MouseButton("back")

        self.button_changed: Event[MouseButtonChanged] = Event()
        self.button_pressed: Event[MouseButtonChanged] = Event()
        self.button_released: Event[MouseButtonChanged] = Event()

    def move(self, position: IVector2, delta: IVector2) -> None:
        self.position = position
        self.moved(
            {"position": self.position, "world_position": self.world_position, "delta": delta}
        )

    def scroll(self, delta: IVector2) -> None:
        self.scrolled({"delta": delta})
        if delta.y:
            y_data: MouseScrolledDirection = {"delta": delta.y}
            self.scrolled_vertically(y_data)
            if delta.y > 0:
                self.scrolled_up(y_data)
            else:
                assert delta.y < 0
                self.scrolled_down(y_data)
        if delta.x:
            x_data: MouseScrolledDirection = {"delta": delta.x}
            self.scrolled_horizontally(x_data)
            if delta.x > 0:
                self.scrolled_right(x_data)
            else:
                assert delta.x < 0
                self.scrolled_left(x_data)

    def change_button(self, name: MouseButtonName, is_pressed: bool) -> None:
        button: MouseButton = getattr(self, name)
        button.is_pressed = is_pressed
        event_data: MouseButtonChanged = {
            "button": button,
            "is_pressed": is_pressed,
            "position": self.position,
            "world_position": self.world_position,
        }
        self.button_changed(event_data)
        button.changed(event_data)
        if is_pressed:
            self.button_pressed(event_data)
            button.pressed(event_data)
        else:
            self.button_released(event_data)
            button.released(event_data)

    @property
    def world_position(self) -> IVector2:
        window = get_window()
        return window.convert_screen_coordinate_to_world_coordinate(self.position)


class MouseMoved(TypedDict):
    position: IVector2
    world_position: IVector2
    delta: IVector2


class MouseScrolled(TypedDict):
    delta: IVector2


class MouseScrolledDirection(TypedDict):
    delta: int


class MouseButtonChanged(TypedDict):
    button: MouseButton
    is_pressed: bool
    position: IVector2
    world_position: IVector2
