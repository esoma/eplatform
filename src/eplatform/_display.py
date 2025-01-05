__all__ = ["Display", "discover_displays", "forget_displays", "get_displays"]

from enum import Enum
from typing import Collection
from typing import Generator

from egeometry import IRectangle
from emath import IVector2

from . import _eplatform
from ._eplatform import get_sdl_displays
from ._type import SdlDisplayId


class DisplayDisconnectedError(RuntimeError):
    pass


class DisplayOrientation(Enum):
    NONE = _eplatform.SDL_ORIENTATION_UNKNOWN
    LANDSCAPE = _eplatform.SDL_ORIENTATION_LANDSCAPE
    LANDSCAPE_FLIPPED = _eplatform.SDL_ORIENTATION_LANDSCAPE_FLIPPED
    PORTRAIT = _eplatform.SDL_ORIENTATION_PORTRAIT
    PORTRAIT_FLIPPED = _eplatform.SDL_ORIENTATION_PORTRAIT_FLIPPED


class DisplayFullscreenMode:
    def __init__(self, size: IVector2, refresh_rate: float) -> None:
        self._size = size
        self._refresh_rate = refresh_rate

    def __repr__(self) -> str:
        return (
            f"<DisplayFullscreenMode "
            f"{self._size.x!r}x{self._size.y}px "
            f"@ {self._refresh_rate:.1f} hertz"
            f">"
        )

    @property
    def size(self) -> IVector2:
        return self._size

    @property
    def refresh_rate(self) -> float:
        return self._refresh_rate


class Display:
    _sdl_display: SdlDisplayId | None = None
    _name: str = ""
    _orientation: DisplayOrientation = DisplayOrientation.NONE
    _bounds: IRectangle = IRectangle(IVector2(0), IVector2(1))
    _refresh_rate: float | None = None
    _fullscreen_modes: tuple[DisplayFullscreenMode, ...] = ()

    def __repr__(self) -> str:
        if self._sdl_display is None:
            return "<Display>"
        assert self._name is not None
        return f"<Display {self._name!r}>"

    @property
    def is_connected(self) -> bool:
        return self._sdl_display is not None

    @property
    def fullscreen_modes(self) -> Collection[DisplayFullscreenMode]:
        if not self.is_connected:
            raise DisplayDisconnectedError()
        return self._fullscreen_modes

    @property
    def name(self) -> str:
        if not self.is_connected:
            raise DisplayDisconnectedError()
        return self._name

    @property
    def orientation(self) -> DisplayOrientation:
        if not self.is_connected:
            raise DisplayDisconnectedError()
        return self._orientation

    @property
    def bounds(self) -> IRectangle:
        if not self.is_connected:
            raise DisplayDisconnectedError()
        return self._bounds

    @property
    def refresh_rate(self) -> float | None:
        if not self.is_connected:
            raise DisplayDisconnectedError()
        return self._refresh_rate


_displays: dict[SdlDisplayId, Display] = {}


def get_displays() -> Generator[Display, None, None]:
    yield from _displays.values()


def connect_display(
    display: Display,
    sdl_display: SdlDisplayId,
    name: str,
    orientation: DisplayOrientation,
    bounds: IRectangle,
    refresh_rate: float,
    fullscreen_modes: tuple[DisplayFullscreenMode, ...],
) -> None:
    assert display._sdl_display is None
    assert sdl_display not in _displays
    display._sdl_display = sdl_display
    display._name = name
    display._orientation = orientation
    display._bounds = bounds
    display._refresh_rate = refresh_rate if refresh_rate > 0 else None
    display._fullscreen_modes = fullscreen_modes
    _displays[sdl_display] = display


def disconnect_display(display: Display) -> None:
    assert display._sdl_display is not None
    sdl_display = display._sdl_display
    display._sdl_display = None
    del _displays[sdl_display]


def discover_displays() -> None:
    for (
        sdl_display,
        display_name,
        display_orientation,
        display_x,
        display_y,
        display_w,
        display_h,
        display_refresh_rate,
        display_fullscreen_modes,
    ) in get_sdl_displays():
        display = Display()
        connect_display(
            display,
            sdl_display,
            display_name,
            DisplayOrientation(display_orientation),
            IRectangle(IVector2(display_x, display_y), IVector2(display_w, display_h)),
            display_refresh_rate,
            tuple(
                DisplayFullscreenMode(IVector2(w, h), rr) for w, h, rr in display_fullscreen_modes
            ),
        )


def forget_displays() -> None:
    for display in list(_displays.values()):
        disconnect_display(display)
