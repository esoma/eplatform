from __future__ import annotations

__all__ = ["get_window", "get_gl_version", "Platform", "Window", "WindowBufferSynchronization"]

# eplatform
from ._platform import Platform
from ._platform import get_gl_version
from ._platform import get_window
from ._window import Window
from ._window import WindowBufferSynchronization
