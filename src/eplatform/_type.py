__all__ = [
    "SdlDisplayId",
    "SdlEventType",
    "SdlGlContext",
    "SdlMouseButton",
    "SdlScancode",
    "SdlWindow",
]

from typing import NewType

SdlGlContext = NewType("SdlGlContext", object)
SdlWindow = NewType("SdlWindow", object)
SdlEventType = NewType("SdlEventType", int)
SdlMouseButton = NewType("SdlMouseButton", int)
SdlScancode = NewType("SdlScancode", int)
SdlDisplayId = NewType("SdlDisplayId", int)
