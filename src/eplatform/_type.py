__all__ = [
    "SdlDisplayId",
    "SdlDisplayOrientation",
    "SdlEventType",
    "SdlGamepadAxis",
    "SdlGamepadBindingType",
    "SdlGamepadButton",
    "SdlGamepadButtonLabel",
    "SdlGlContext",
    "SdlJoystickId",
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
SdlDisplayOrientation = NewType("SdlDisplayOrientation", int)
SdlJoystickId = NewType("SdlJoystickId", int)
SdlGamepadButton = NewType("SdlGamepadButton", int)
SdlGamepadButtonLabel = NewType("SdlGamepadButtonLabel", int)
SdlGamepadAxis = NewType("SdlGamepadAxis", int)
SdlGamepadBindingType = NewType("SdlGamepadBindingType", int)
