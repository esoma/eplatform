from __future__ import annotations

__all__ = ["Window", "WindowBufferSynchronization"]

# eevent
from eevent import Event

# emath
from emath import FMatrix4
from emath import FVector4
from emath import IVector2

# pysdl2
from sdl2 import SDL_GL_SetSwapInterval
from sdl2 import SDL_GL_SwapWindow
from sdl2 import SDL_WINDOW_HIDDEN
from sdl2 import SDL_WINDOW_OPENGL
from sdl2.ext import Window as _Window

# python
from enum import Enum


class WindowBufferSynchronization(Enum):
    IMMEDIATE = 0
    VSYNC = 1
    ADAPTIVE_VSYNC = -1


class Window(_Window):
    def __init__(self) -> None:
        super().__init__("", (200, 200), flags=SDL_WINDOW_HIDDEN | SDL_WINDOW_OPENGL)
        self.closed: Event[None] = Event()
        self.screen_space_to_world_space_transform = FMatrix4(1)

    def refresh(
        self, synchronization: WindowBufferSynchronization = WindowBufferSynchronization.IMMEDIATE
    ) -> None:
        while True:
            if SDL_GL_SetSwapInterval(synchronization.value) == 0:
                break
            # not all systems support adaptive vsync, so try regular vsync
            # instead
            if synchronization == WindowBufferSynchronization.ADAPTIVE_VSYNC:
                synchronization = WindowBufferSynchronization.VSYNC
            else:
                # not all systems are double buffered, so setting any swap
                # interval will result in an error
                # we don't actually need to swap the window in this case
                return
        SDL_GL_SwapWindow(self.window)

    @property
    def size(self) -> IVector2:
        return IVector2(*super().size)

    @size.setter
    def size(self, value: IVector2) -> None:
        super(Window, type(self)).size.fset(self, tuple(value))

    def convert_screen_coordinate_to_world_coordinate(self, coord: IVector2) -> IVector2:
        clip_space_position = FVector4(
            (coord.x / self.size.x) * 2 - 1, -(coord.y / self.size.y) * 2 + 1, 0, 1
        )
        world_space_mouse_position = (
            self.screen_space_to_world_space_transform @ clip_space_position
        )
        return IVector2(int(world_space_mouse_position.x), int(world_space_mouse_position.y))
