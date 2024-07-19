from __future__ import annotations

__all__ = [
    "Platform",
    "get_color_bits",
    "get_depth_bits",
    "get_keyboard",
    "get_mouse",
    "get_stencil_bits",
    "get_window",
]

# eplatform
from ._keyboard import Keyboard

# pysdl2
from sdl2 import SDL_GL_ALPHA_SIZE
from sdl2 import SDL_GL_BLUE_SIZE
from sdl2 import SDL_GL_CONTEXT_MAJOR_VERSION
from sdl2 import SDL_GL_CONTEXT_MINOR_VERSION
from sdl2 import SDL_GL_CONTEXT_PROFILE_CORE
from sdl2 import SDL_GL_CONTEXT_PROFILE_MASK
from sdl2 import SDL_GL_CreateContext
from sdl2 import SDL_GL_DEPTH_SIZE
from sdl2 import SDL_GL_DeleteContext
from sdl2 import SDL_GL_GREEN_SIZE
from sdl2 import SDL_GL_GetAttribute
from sdl2 import SDL_GL_RED_SIZE
from sdl2 import SDL_GL_STENCIL_SIZE
from sdl2 import SDL_GL_SetAttribute
from sdl2 import SDL_GetError
from sdl2 import SDL_INIT_VIDEO
from sdl2 import SDL_InitSubSystem
from sdl2 import SDL_QuitSubSystem

# python
import ctypes
from typing import Any
from typing import Callable
from typing import ClassVar
from typing import Final
from typing import Self
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    # eplatform
    from ._mouse import Mouse
    from ._window import Window

_SDL_SUB_SYSTEMS: Final = SDL_INIT_VIDEO


class Platform:
    _deactivate_callbacks: ClassVar[list[Callable[[], None]]] = []
    _singleton: ClassVar[Self | None] = None
    _window: Window | None = None
    _mouse: Mouse | None = None
    _keyboard: Keyboard | None = None
    _gl_context: Any = None
    _gl_version: tuple[int, int] | None = None
    _color_bits: tuple[int, int, int, int] | None = None
    _depth_bits: int | None = None
    _stencil_bits: int | None = None

    def __init__(
        self,
        *,
        window_cls: type[Window] | None = None,
        mouse_cls: type[Mouse] | None = None,
        keyboard_cls: type[Keyboard] | None = None,
    ) -> None:
        if window_cls is None:
            # eplatform
            from ._window import Window

            self._window_cls = Window
        else:
            self._window_cls = window_cls

        if mouse_cls is None:
            # eplatform
            from ._mouse import Mouse

            self._mouse_cls = Mouse
        else:
            self._mouse_cls = mouse_cls

        if keyboard_cls is None:
            self._keyboard_cls = Keyboard
        else:
            self._keyboard_cls = keyboard_cls

    def __enter__(self) -> None:
        if Platform._singleton:
            raise RuntimeError("platform already active")

        SDL_InitSubSystem(_SDL_SUB_SYSTEMS)
        self._window = self._window_cls()
        self._mouse = self._mouse_cls()
        self._keyboard = self._keyboard_cls()
        self._setup_open_gl()
        Platform._singleton = self

    def __exit__(self, *args: Any, **kwargs: Any) -> None:
        if Platform._singleton is not self:
            raise RuntimeError("platform instance is not active")

        for callback in self._deactivate_callbacks:
            callback()

        self._teardown_open_gl()

        assert self._window is not None
        self._window.close()
        self._window = None

        SDL_QuitSubSystem(_SDL_SUB_SYSTEMS)
        Platform._singleton = None

    def _setup_open_gl(self) -> None:
        assert self._window is not None

        for major, minor in [
            (4, 6),
            (4, 5),
            (4, 4),
            (4, 3),
            (4, 2),
            (4, 1),
            (4, 0),
            (3, 3),
            (3, 2),
            (3, 1),
        ]:
            if SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, major) != 0:
                raise RuntimeError(SDL_GetError().decode("utf8"))
            if SDL_GL_SetAttribute(SDL_GL_CONTEXT_MINOR_VERSION, minor) != 0:
                raise RuntimeError(SDL_GetError().decode("utf8"))
            if SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_CORE) != 0:
                raise RuntimeError(SDL_GetError().decode("utf8"))
            self._gl_context = SDL_GL_CreateContext(self._window.window)
            if self._gl_context is not None:
                break
        if self._gl_context is None:
            raise RuntimeError(SDL_GetError().decode("utf8"))

        bits = ctypes.c_int(0)
        SDL_GL_GetAttribute(SDL_GL_RED_SIZE, ctypes.byref(bits))
        red_bits = bits.value
        SDL_GL_GetAttribute(SDL_GL_GREEN_SIZE, ctypes.byref(bits))
        green_bits = bits.value
        SDL_GL_GetAttribute(SDL_GL_BLUE_SIZE, ctypes.byref(bits))
        blue_bits = bits.value
        SDL_GL_GetAttribute(SDL_GL_ALPHA_SIZE, ctypes.byref(bits))
        alpha_bits = bits.value
        SDL_GL_GetAttribute(SDL_GL_DEPTH_SIZE, ctypes.byref(bits))
        depth_bits = bits.value
        SDL_GL_GetAttribute(SDL_GL_STENCIL_SIZE, ctypes.byref(bits))
        stencil_bits = bits.value
        self._color_bits = (red_bits, green_bits, blue_bits, alpha_bits)
        self._depth_bits = depth_bits
        self._stencil_bits = stencil_bits

    def _teardown_open_gl(self) -> None:
        if self._gl_context is not None:
            SDL_GL_DeleteContext(self._gl_context)
            self._gl_context = None
            self._gl_version = None

    @classmethod
    def register_deactivate_callback(cls, callback: Callable[[], None]) -> Callable[[], None]:
        cls._deactivate_callbacks.append(callback)
        return callback


def get_window() -> Window:
    if Platform._singleton is None:
        raise RuntimeError("platform is not active")
    window = Platform._singleton._window
    assert window is not None
    return window


def get_mouse() -> Mouse:
    if Platform._singleton is None:
        raise RuntimeError("platform is not active")
    mouse = Platform._singleton._mouse
    assert mouse is not None
    return mouse


def get_keyboard() -> Keyboard:
    if Platform._singleton is None:
        raise RuntimeError("platform is not active")
    keyboard = Platform._singleton._keyboard
    assert keyboard is not None
    return keyboard


def get_color_bits() -> tuple[int, int, int, int]:
    if Platform._singleton is None:
        raise RuntimeError("platform is not active")
    color_bits = Platform._singleton._color_bits
    assert color_bits is not None
    return color_bits


def get_depth_bits() -> int:
    if Platform._singleton is None:
        raise RuntimeError("platform is not active")
    depth_bits = Platform._singleton._depth_bits
    assert depth_bits is not None
    return depth_bits


def get_stencil_bits() -> int:
    if Platform._singleton is None:
        raise RuntimeError("platform is not active")
    stencil_bits = Platform._singleton._stencil_bits
    assert stencil_bits is not None
    return stencil_bits
