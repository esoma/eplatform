from __future__ import annotations

__all__ = [
    "blur_window",
    "close_window",
    "delete_window",
    "focus_window",
    "get_sdl_window",
    "hide_window",
    "input_window_text",
    "move_window",
    "resize_window",
    "show_window",
    "Window",
    "WindowBufferSynchronization",
    "WindowDestroyedError",
    "WindowMoved",
    "WindowResized",
    "WindowTextInputted",
    "WindowVisibilityChanged",
]

from contextlib import contextmanager
from enum import Enum
from typing import Generator
from typing import TypedDict

from eevent import Event
from egeometry import IRectangle
from emath import FMatrix4
from emath import FVector4
from emath import IVector2

from ._display import Display
from ._display import DisplayMode
from ._display import get_sdl_display_id
from ._eplatform import center_sdl_window
from ._eplatform import create_sdl_window
from ._eplatform import delete_sdl_window
from ._eplatform import disable_sdl_window_text_input
from ._eplatform import enable_sdl_window_text_input
from ._eplatform import hide_sdl_window
from ._eplatform import set_sdl_window_always_on_top
from ._eplatform import set_sdl_window_border
from ._eplatform import set_sdl_window_fullscreen
from ._eplatform import set_sdl_window_not_fullscreen
from ._eplatform import set_sdl_window_size
from ._eplatform import show_sdl_window
from ._eplatform import swap_sdl_window
from ._type import SdlWindow


class WindowBufferSynchronization(Enum):
    IMMEDIATE = 0
    VSYNC = 1
    ADAPTIVE_VSYNC = -1


class WindowTextInputted(TypedDict):
    text: str


class WindowResized(TypedDict):
    size: IVector2


class WindowMoved(TypedDict):
    position: IVector2


class WindowVisibilityChanged(TypedDict):
    is_visible: bool


class WindowDestroyedError(RuntimeError):
    pass


class Window:
    _sdl_window: SdlWindow | None = None

    def __init__(self) -> None:
        self._sdl_window, x, y = create_sdl_window()

        self._position = IVector2(x, y)
        self.moved: Event[WindowMoved] = Event()

        self.closed: Event[None] = Event()
        self.text_inputted: Event[WindowTextInputted] = Event()

        self.screen_space_to_world_space_transform = FMatrix4(1)

        self._size = IVector2(200, 200)
        self.resized: Event[WindowResized] = Event()

        self._is_visible = False
        self.visibility_changed: Event[WindowVisibilityChanged] = Event()
        self.shown: Event[WindowVisibilityChanged] = Event()
        self.hidden: Event[WindowVisibilityChanged] = Event()

        self._is_focused = False
        self.focused: Event[None] = Event()
        self.blurred: Event[None] = Event()

        self._is_bordered = True
        self._is_always_on_top = False
        self._is_fullscreen = False

    def __del__(self) -> None:
        delete_window(self)

    def enable_text_input(self, rect: IRectangle, *, cursor_position: int = 0) -> None:
        if self._sdl_window is None:
            raise WindowDestroyedError()
        enable_sdl_window_text_input(
            self._sdl_window,
            rect.position.x,
            rect.position.y,
            rect.size.x,
            rect.size.y,
            cursor_position,
        )

    def disable_text_input(self) -> None:
        if not self._sdl_window:
            return
        disable_sdl_window_text_input(self._sdl_window)

    @contextmanager
    def text_input(
        self, rect: IRectangle, *, cursor_position: int = 0
    ) -> Generator[None, None, None]:
        self.enable_text_input(rect, cursor_position=cursor_position)
        yield
        self.disable_text_input()

    def show(self) -> None:
        if self._sdl_window is None:
            raise WindowDestroyedError()
        show_sdl_window(self._sdl_window)

    def hide(self) -> None:
        if not self._sdl_window:
            return
        hide_sdl_window(self._sdl_window)

    @property
    def is_visible(self) -> bool:
        return self._is_visible

    def center(self) -> None:
        if self._sdl_window is None:
            raise WindowDestroyedError()
        center_sdl_window(self._sdl_window)

    def refresh(
        self, synchronization: WindowBufferSynchronization = WindowBufferSynchronization.IMMEDIATE
    ) -> None:
        if self._sdl_window is None:
            raise WindowDestroyedError()
        swap_sdl_window(self._sdl_window, synchronization.value)

    def resize(self, value: IVector2) -> None:
        if self._sdl_window is None:
            raise WindowDestroyedError()
        set_sdl_window_size(self._sdl_window, value)

    @property
    def position(self) -> IVector2:
        return self._position

    @property
    def size(self) -> IVector2:
        return self._size

    @property
    def is_bordered(self) -> bool:
        return self._is_bordered

    def show_border(self) -> None:
        if self._sdl_window is None:
            raise WindowDestroyedError()
        set_sdl_window_border(self._sdl_window, True)
        self._is_bordered = True

    def hide_border(self) -> None:
        if self._sdl_window is None:
            raise WindowDestroyedError()
        set_sdl_window_border(self._sdl_window, False)
        self._is_bordered = False

    @property
    def is_always_on_top(self) -> bool:
        return self._is_always_on_top

    def force_always_on_top(self) -> None:
        if self._sdl_window is None:
            raise WindowDestroyedError()
        set_sdl_window_always_on_top(self._sdl_window, True)
        self._is_always_on_top = True

    def allow_not_on_top(self) -> None:
        if self._sdl_window is None:
            raise WindowDestroyedError()
        set_sdl_window_always_on_top(self._sdl_window, False)
        self._is_always_on_top = False

    def convert_screen_coordinate_to_world_coordinate(self, coord: IVector2) -> IVector2:
        clip_space_position = FVector4(
            (coord.x / self.size.x) * 2 - 1, -(coord.y / self.size.y) * 2 + 1, 0, 1
        )
        world_space_mouse_position = (
            self.screen_space_to_world_space_transform @ clip_space_position
        )
        return IVector2(int(world_space_mouse_position.x), int(world_space_mouse_position.y))

    @property
    def is_fullscreen(self) -> bool:
        return self._is_fullscreen

    def fullscreen(self, display: Display, mode: DisplayMode) -> None:
        if self._sdl_window is None:
            raise WindowDestroyedError()
        sdl_display_id = get_sdl_display_id(display)
        set_sdl_window_fullscreen(
            self._sdl_window, sdl_display_id, mode.size.x, mode.size.y, mode.refresh_rate
        )
        self._is_fullscreen = True

    def window(self) -> None:
        if self._sdl_window is None:
            raise WindowDestroyedError()
        set_sdl_window_not_fullscreen(self._sdl_window)
        self._is_fullscreen = False

    @property
    def is_focused(self) -> bool:
        return self._is_focused


def get_sdl_window(window: Window) -> SdlWindow:
    assert window._sdl_window is not None
    return window._sdl_window


def delete_window(window: Window) -> None:
    if window._sdl_window is None:
        return
    delete_sdl_window(window._sdl_window)
    window._sdl_window = None


def close_window(window: Window) -> None:
    window.closed(None)


def input_window_text(window: Window, text: str) -> None:
    window.text_inputted({"text": text})


def show_window(window: Window) -> None:
    window._is_visible = True
    event_data: WindowVisibilityChanged = {"is_visible": True}
    window.visibility_changed(event_data)
    window.shown(event_data)


def hide_window(window: Window) -> None:
    window._is_visible = False
    event_data: WindowVisibilityChanged = {"is_visible": False}
    window.visibility_changed(event_data)
    window.hidden(event_data)


def resize_window(window: Window, size: IVector2) -> None:
    window._size = size
    window.resized({"size": size})


def move_window(window: Window, position: IVector2) -> None:
    window._position = position
    window.moved({"position": position})


def focus_window(window: Window) -> None:
    window._is_focused = True
    window.focused(None)


def blur_window(window: Window) -> None:
    window._is_focused = False
    window.blurred(None)
