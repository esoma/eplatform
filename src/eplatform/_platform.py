from __future__ import annotations

__all__ = [
    "Platform",
    "get_gl_version",
    "get_window",
]

# eplatform
from ._window import Window

# pyopengl
from OpenGL.GL import GL_VERSION
from OpenGL.GL import glGetString

# pysdl2
from sdl2 import SDL_GL_CONTEXT_MAJOR_VERSION
from sdl2 import SDL_GL_CONTEXT_MINOR_VERSION
from sdl2 import SDL_GL_CONTEXT_PROFILE_CORE
from sdl2 import SDL_GL_CONTEXT_PROFILE_MASK
from sdl2 import SDL_GL_CreateContext
from sdl2 import SDL_GL_DeleteContext
from sdl2 import SDL_GL_SetAttribute
from sdl2 import SDL_GetError
from sdl2 import SDL_INIT_VIDEO
from sdl2 import SDL_InitSubSystem
from sdl2 import SDL_QuitSubSystem

# python
from typing import Any
from typing import Callable
from typing import ClassVar
from typing import Final
from typing import Self

_SDL_SUB_SYSTEMS: Final = SDL_INIT_VIDEO


class Platform:
    _deactivate_callbacks: ClassVar[list[Callable[[], None]]] = []
    _singleton: ClassVar[Self | None] = None
    _window: Window | None = None
    _gl_context: Any = None
    _gl_version: tuple[int, int] | None = None

    def __enter__(self) -> None:
        if self._singleton:
            raise RuntimeError("platform already active")

        SDL_InitSubSystem(_SDL_SUB_SYSTEMS)
        self._window = Window()
        self._setup_open_gl()
        self.__class__._singleton = self

    def __exit__(self, *args: Any, **kwargs: Any) -> None:
        if self._singleton is not self:
            raise RuntimeError("platform instance is not active")

        for callback in self._deactivate_callbacks:
            callback()

        self._teardown_open_gl()

        assert self._window is not None
        self._window.close()
        self._window = None

        SDL_QuitSubSystem(_SDL_SUB_SYSTEMS)
        self.__class__._singleton = None

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

        gl_version = glGetString(GL_VERSION).decode("utf8")
        self._gl_version: tuple[int, int] = tuple(  # type: ignore
            int(v) for v in gl_version.split(" ")[0].split(".")[:2]
        )

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


def get_gl_version() -> tuple[int, int]:
    if Platform._singleton is None:
        raise RuntimeError("platform is not active")
    gl_version = Platform._singleton._gl_version
    assert gl_version is not None
    return gl_version