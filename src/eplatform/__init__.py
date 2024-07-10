from __future__ import annotations

__all__ = [
    "get_mouse",
    "get_window",
    "get_gl_version",
    "Mouse",
    "MouseButton",
    "MouseButtonName",
    "MouseMoved",
    "MouseScrolled",
    "MouseScrolledDirection",
    "Platform",
    "Window",
    "WindowBufferSynchronization",
]

# eplatform
from ._mouse import Mouse
from ._mouse import MouseButton
from ._mouse import MouseButtonName
from ._mouse import MouseMoved
from ._mouse import MouseScrolled
from ._mouse import MouseScrolledDirection
from ._platform import Platform
from ._platform import get_gl_version
from ._platform import get_mouse
from ._platform import get_window
from ._window import Window
from ._window import WindowBufferSynchronization
