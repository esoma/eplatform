from __future__ import annotations

__all__ = [
    "get_sdl_window",
    "Window",
    "WindowBufferSynchronization",
    "WindowTextInputted",
    "WindowDestroyedError",
]

# eplatform
from ._eplatform import center_sdl_window
from ._eplatform import create_sdl_window
from ._eplatform import delete_sdl_window
from ._eplatform import disable_sdl_window_text_input
from ._eplatform import enable_sdl_window_text_input
from ._eplatform import hide_sdl_window
from ._eplatform import set_sdl_window_size
from ._eplatform import show_sdl_window
from ._eplatform import swap_sdl_window
from ._type import SdlWindow

# eevent
from eevent import Event

# egeometry
from egeometry import IRectangle

# emath
from emath import FMatrix4
from emath import FVector4
from emath import IVector2

# python
from contextlib import contextmanager
from enum import Enum
from typing import Generator
from typing import TypedDict


class WindowBufferSynchronization(Enum):
    IMMEDIATE = 0
    VSYNC = 1
    ADAPTIVE_VSYNC = -1


class WindowTextInputted(TypedDict):
    text: str


class WindowResized(TypedDict):
    size: IVector2


class WindowVisibilityChanged(TypedDict):
    is_visible: bool


class WindowDestroyedError(RuntimeError):
    pass


class Window:
    _sdl_window: SdlWindow | None

    def __init__(self) -> None:
        self._sdl_window = create_sdl_window()

        self.closed: Event[None] = Event()
        self.text_inputted: Event[WindowTextInputted] = Event()

        self.screen_space_to_world_space_transform = FMatrix4(1)

        self._size = IVector2(200, 200)
        self.resized: Event[WindowResized] = Event()

        self._is_visible = False
        self.visibility_changed: Event[WindowVisibilityChanged] = Event()
        self.shown: Event[WindowVisibilityChanged] = Event()
        self.hidden: Event[WindowVisibilityChanged] = Event()

    def __del__(self) -> None:
        self._delete_sdl_window()

    def close(self) -> None:
        self.closed(None)

    def _delete_sdl_window(self) -> None:
        if self._sdl_window is None:
            return
        delete_sdl_window(self._sdl_window)
        self._sdl_window = None

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

    def input_text(self, text: str) -> None:
        self.text_inputted({"text": text})

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

    @is_visible.setter
    def is_visible(self, value: bool) -> None:
        self._is_visible = value
        event_data: WindowVisibilityChanged = {"is_visible": value}
        self.visibility_changed(event_data)
        if value:
            self.shown(event_data)
        else:
            self.hidden(event_data)

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
    def size(self) -> IVector2:
        return self._size

    @size.setter
    def size(self, value: IVector2) -> None:
        self._size = value
        self.resized({"size": value})

    def convert_screen_coordinate_to_world_coordinate(self, coord: IVector2) -> IVector2:
        clip_space_position = FVector4(
            (coord.x / self.size.x) * 2 - 1, -(coord.y / self.size.y) * 2 + 1, 0, 1
        )
        world_space_mouse_position = (
            self.screen_space_to_world_space_transform @ clip_space_position
        )
        return IVector2(int(world_space_mouse_position.x), int(world_space_mouse_position.y))


def get_sdl_window(window: Window) -> SdlWindow:
    assert window._sdl_window is not None
    return window._sdl_window
