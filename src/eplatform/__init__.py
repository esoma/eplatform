from __future__ import annotations

__all__ = [
    "EventLoop",
    "get_color_bits",
    "get_depth_bits",
    "get_keyboard",
    "get_mouse",
    "get_stencil_bits",
    "get_window",
    "Keyboard",
    "KeyboardKey",
    "KeyboardKeyChanged",
    "KeyboardKeyName",
    "Mouse",
    "MouseButton",
    "MouseButtonChanged",
    "MouseButtonName",
    "MouseMoved",
    "MouseScrolled",
    "MouseScrolledDirection",
    "Platform",
    "Window",
    "WindowBufferSynchronization",
]

# eplatform
from ._event_loop import EventLoop
from ._keyboard import Keyboard
from ._keyboard import KeyboardKey
from ._keyboard import KeyboardKeyChanged
from ._keyboard import KeyboardKeyName
from ._mouse import Mouse
from ._mouse import MouseButton
from ._mouse import MouseButtonChanged
from ._mouse import MouseButtonName
from ._mouse import MouseMoved
from ._mouse import MouseScrolled
from ._mouse import MouseScrolledDirection
from ._platform import Platform
from ._platform import get_color_bits
from ._platform import get_depth_bits
from ._platform import get_keyboard
from ._platform import get_mouse
from ._platform import get_stencil_bits
from ._platform import get_window
from ._window import Window
from ._window import WindowBufferSynchronization
