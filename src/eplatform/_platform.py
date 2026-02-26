from __future__ import annotations

__all__ = [
    "Platform",
    "get_clipboard",
    "get_controllers",
    "get_displays",
    "get_keyboard",
    "get_mouse",
    "get_window",
    "set_clipboard",
]

import logging
import os
from enum import IntFlag
from typing import TYPE_CHECKING
from typing import Any
from typing import Callable
from typing import ClassVar
from typing import Final
from typing import Generator
from typing import Self
from typing import Sequence

from emath import IVector2

from ._controller import Controller
from ._controller import discover_controllers
from ._controller import forget_controllers
from ._controller import get_controllers as _get_controllers
from ._display import Display
from ._display import discover_displays
from ._display import forget_displays
from ._display import get_displays as _get_displays
from ._eplatform import GRAPHICS_LIBRARY_OPEN_GL
from ._eplatform import clear_sdl_events
from ._eplatform import create_sdl_gl_context
from ._eplatform import create_sdl_vulkan_surface
from ._eplatform import create_sdl_window
from ._eplatform import create_vulkan_debug_messenger
from ._eplatform import create_vulkan_instance
from ._eplatform import deinitialize_sdl
from ._eplatform import delete_sdl_gl_context
from ._eplatform import delete_sdl_vulkan_surface
from ._eplatform import delete_vulkan_debug_messenger
from ._eplatform import delete_vulkan_instance
from ._eplatform import get_clipboard as _get_clipboard
from ._eplatform import get_gl_attrs
from ._eplatform import initialize_sdl
from ._eplatform import set_clipboard as _set_clipboard
from ._keyboard import Keyboard
from ._type import VkDebugUtilsMessenger
from ._type import VkInstance
from ._type import VkSurface
from ._window import OpenGlWindow
from ._window import VulkanWindow
from ._window import Window
from ._window import delete_window
from ._window import get_sdl_window

if TYPE_CHECKING:
    from ._mouse import Mouse


_GL_VERSIONS: Final[tuple[tuple[int, int], ...]] = (
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
)


class VulkanMessageSeverity(IntFlag):
    VERBOSE = 0x00000001
    INFO = 0x00000010
    WARNING = 0x00000100
    ERROR = 0x00001000


class VulkanMessageType(IntFlag):
    GENERAL = 0x00000001
    VALIDATION = 0x00000002
    PERFORMANCE = 0x00000004


def log_vulkan_message(severity: int, type: int, message: str) -> None:
    if severity & VulkanMessageSeverity.ERROR.value:
        log_level = logging.ERROR
    elif severity & VulkanMessageSeverity.WARNING.value:
        log_level = logging.WARNING
    elif severity & VulkanMessageSeverity.INFO.value:
        log_level = logging.INFO
    else:
        log_level = logging.DEBUG
    if type & VulkanMessageType.PERFORMANCE.value:
        log = logging.getLogger("eplatform.vulkan.performance")
    elif type & VulkanMessageType.VALIDATION.value:
        log = logging.getLogger("eplatform.vulkan.validation")
    else:
        log = logging.getLogger("eplatform.vulkan")
    log.log(log_level, message)


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
    _vk_instance: VkInstance | None = None
    _vk_surface: VkSurface | None = None
    _vk_debug_messenger: VkDebugUtilsMessenger | None = None

    def __init__(
        self,
        *,
        window_cls: type[Window] | None = None,
        mouse_cls: type[Mouse] | None = None,
        keyboard_cls: type[Keyboard] | None = None,
        vulkan_layers: Sequence[str] = (),
        vulkan_extensions: Sequence[str] = (),
        vulkan_message_callback: Callable[[int, int, str], None] | None = None,
        open_gl_version_min: tuple[int, int] = _GL_VERSIONS[-1],
        open_gl_version_max: tuple[int, int] = _GL_VERSIONS[0],
    ) -> None:
        if __debug__ and vulkan_message_callback is None:
            vulkan_message_callback = log_vulkan_message

        self._vulkan_layers = vulkan_layers
        self._vulkan_extensions = vulkan_extensions
        self._vulkan_message_callback = vulkan_message_callback
        self._gl_version_min = open_gl_version_min
        self._gl_version_max = open_gl_version_max

        if window_cls is None:
            self._window_cls = Window
        else:
            self._window_cls = window_cls

        if mouse_cls is None:
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
        initialize_sdl()
        if issubclass(self._window_cls, VulkanWindow):
            self._window = self._window_cls()
            self._setup_vulkan()
        elif issubclass(self._window_cls, OpenGlWindow):
            for gl_version in _GL_VERSIONS:
                if gl_version > self._gl_version_max:
                    continue
                if gl_version < self._gl_version_min:
                    continue
                gl_major_version, gl_minor_version = gl_version
                self._window = self._window_cls(
                    major_version=gl_major_version, minor_version=gl_minor_version
                )
                try:
                    self._setup_open_gl()
                except RuntimeError as ex:
                    if str(ex) == "unable to create open gl context":
                        if self._window is not None:
                            delete_window(self._window)
                        self._window = None
                        continue
                    raise
                break
            else:
                raise RuntimeError("unable to create open gl context")
            self._gl_version = gl_version
        else:
            self._window = self._window_cls()
        self._mouse = self._mouse_cls()
        self._keyboard = self._keyboard_cls()
        discover_displays()
        discover_controllers()
        clear_sdl_events()
        Platform._singleton = self

    def __exit__(self, *args: Any, **kwargs: Any) -> None:
        if Platform._singleton is not self:
            raise RuntimeError("platform instance is not active")

        for callback in self._deactivate_callbacks:
            callback()

        self._teardown_open_gl()
        self._teardown_vulkan()
        forget_controllers()
        forget_displays()
        assert self._window is not None
        delete_window(self._window)
        self._window = None

        deinitialize_sdl()
        Platform._singleton = None

    def _setup_open_gl(self) -> None:
        assert self._window is not None
        if not isinstance(self._window, OpenGlWindow):
            return
        sdl_window = get_sdl_window(self._window)
        self._gl_context = create_sdl_gl_context(sdl_window)

        r, g, b, a, d, s = get_gl_attrs()
        self._color_bits = (r, g, b, a)
        self._depth_bits = d
        self._stencil_bits = s

    def _teardown_open_gl(self) -> None:
        if self._gl_context is not None:
            delete_sdl_gl_context(self._gl_context)
            self._gl_version = None
            self._gl_context = None
            self._color_bits = None
            self._depth_bits = None
            self._stencil_bits = None

    def _setup_vulkan(self) -> None:
        assert self._window is not None
        if not isinstance(self._window, VulkanWindow):
            return
        self._vk_instance = create_vulkan_instance(
            self._vulkan_layers, self._vulkan_extensions, self._vulkan_message_callback
        )
        if self._vulkan_message_callback:
            self._vk_debug_messenger = create_vulkan_debug_messenger(
                self._vk_instance, self._vulkan_message_callback
            )
        sdl_window = get_sdl_window(self._window)
        self._vk_surface = create_sdl_vulkan_surface(sdl_window, self._vk_instance)

    def _teardown_vulkan(self) -> None:
        if self._vk_surface is not None and self._vk_instance is not None:
            delete_sdl_vulkan_surface(self._vk_instance, self._vk_surface)
            self._vk_surface = None
        if self._vk_debug_messenger is not None:
            assert self._vk_instance is not None
            delete_vulkan_debug_messenger(self._vk_instance, self._vk_debug_messenger)
        if self._vk_instance is not None:
            delete_vulkan_instance(self._vk_instance)
            self._vk_instance = None

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


def get_gl_color_bits() -> tuple[int, int, int, int]:
    assert Platform._singleton is not None
    color_bits = Platform._singleton._color_bits
    assert color_bits is not None
    return color_bits


def get_gl_depth_bits() -> int:
    assert Platform._singleton is not None
    depth_bits = Platform._singleton._depth_bits
    assert depth_bits is not None
    return depth_bits


def get_gl_stencil_bits() -> int:
    assert Platform._singleton is not None
    stencil_bits = Platform._singleton._stencil_bits
    assert stencil_bits is not None
    return stencil_bits


def get_gl_version() -> tuple[int, int]:
    assert Platform._singleton is not None
    gl_version = Platform._singleton._gl_version
    assert gl_version is not None
    return gl_version


def get_vk_instance() -> VkInstance:
    assert Platform._singleton is not None
    vk_instance = Platform._singleton._vk_instance
    assert vk_instance is not None
    return vk_instance


def get_vk_surface() -> VkSurface:
    assert Platform._singleton is not None
    vk_surface = Platform._singleton._vk_surface
    assert vk_surface is not None
    return vk_surface


def get_clipboard() -> str:
    if Platform._singleton is None:
        raise RuntimeError("platform is not active")
    return _get_clipboard()


def set_clipboard(text: str) -> None:
    if Platform._singleton is None:
        raise RuntimeError("platform is not active")
    _set_clipboard(text)


def get_displays() -> Generator[Display, None, None]:
    if Platform._singleton is None:
        raise RuntimeError("platform is not active")
    for display in _get_displays():
        if Platform._singleton is None:
            raise RuntimeError("platform is not active")
        yield display


def get_controllers() -> Generator[Controller, None, None]:
    if Platform._singleton is None:
        raise RuntimeError("platform is not active")
    for controller in _get_controllers():
        if Platform._singleton is None:
            raise RuntimeError("platform is not active")
        yield controller
