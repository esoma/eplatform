from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from egeometry import IRectangle
from emath import IVector2

import eplatform._display
from eplatform import Display
from eplatform import DisplayDisconnectedError
from eplatform import DisplayMode
from eplatform import DisplayOrientation
from eplatform import _eplatform
from eplatform._display import change_display_orientation
from eplatform._display import change_display_position
from eplatform._display import change_display_refresh_rate
from eplatform._display import change_display_size
from eplatform._display import get_displays


@pytest.fixture
def connected_display():
    display = Display()
    display._sdl_display = MagicMock()
    eplatform._display._displays[display._sdl_display] = display
    yield display
    del eplatform._display._displays[display._sdl_display]


def test_create_display():
    display = Display()
    assert not display.is_connected
    assert not list(get_displays())
    assert repr(display) == "<Display>"
    with pytest.raises(DisplayDisconnectedError):
        display.is_primary
    with pytest.raises(DisplayDisconnectedError):
        display.modes
    with pytest.raises(DisplayDisconnectedError):
        display.name
    with pytest.raises(DisplayDisconnectedError):
        display.orientation
    with pytest.raises(DisplayDisconnectedError):
        display.bounds
    with pytest.raises(DisplayDisconnectedError):
        display.refresh_rate


def test_connected_display(connected_display):
    assert connected_display.is_connected


@pytest.mark.parametrize(
    "is_primary, position",
    [
        (True, IVector2(0)),
        (False, IVector2(0, 1)),
        (False, IVector2(1, 0)),
        (False, IVector2(-1)),
        (False, IVector2(100, 100)),
    ],
)
def test_primary_display(connected_display, is_primary, position):
    connected_display._bounds = IRectangle(position, IVector2(1))
    assert connected_display.is_primary == is_primary


@pytest.mark.parametrize("name", ["", "abc"])
def test_name(connected_display, name):
    connected_display._name = name
    assert connected_display.name == name
    assert repr(connected_display) == f"<Display {name!r}>"


@pytest.mark.parametrize("orientation", DisplayOrientation)
def test_orientation(connected_display, orientation):
    connected_display._orientation = orientation
    assert connected_display.orientation == orientation


@pytest.mark.parametrize("refresh_rate", [0.0, 60.12344])
def test_refresh_rate(connected_display, refresh_rate):
    connected_display._refresh_rate = refresh_rate
    assert connected_display.refresh_rate == refresh_rate


@pytest.mark.parametrize(
    "sdl_display_orientation, orientation",
    [
        (_eplatform.SDL_ORIENTATION_UNKNOWN, DisplayOrientation.NONE),
        (_eplatform.SDL_ORIENTATION_LANDSCAPE, DisplayOrientation.LANDSCAPE),
        (_eplatform.SDL_ORIENTATION_LANDSCAPE_FLIPPED, DisplayOrientation.LANDSCAPE_FLIPPED),
        (_eplatform.SDL_ORIENTATION_PORTRAIT, DisplayOrientation.PORTRAIT),
        (_eplatform.SDL_ORIENTATION_PORTRAIT_FLIPPED, DisplayOrientation.PORTRAIT_FLIPPED),
    ],
)
def test_change_display_orientation(connected_display, sdl_display_orientation, orientation):
    with (
        patch.object(
            Display, "orientation_changed", new=MagicMock()
        ) as Display_orientation_changed,
        patch.object(
            connected_display, "orientation_changed", new=MagicMock()
        ) as display_orientation_changed,
    ):
        change_display_orientation(connected_display._sdl_display, sdl_display_orientation)
    assert connected_display.orientation is orientation
    data = {"display": connected_display, "orientation": orientation}
    Display_orientation_changed.assert_called_once_with(data)
    display_orientation_changed.assert_called_once_with(data)


@pytest.mark.parametrize("position", [IVector2(0), IVector2(-100, 100)])
def test_change_display_position(connected_display, position):
    with (
        patch.object(Display, "moved", new=MagicMock()) as Display_moved,
        patch.object(connected_display, "moved", new=MagicMock()) as display_moved,
    ):
        change_display_position(connected_display._sdl_display, position)
    assert connected_display.bounds.position == position
    data = {"display": connected_display, "position": position}
    Display_moved.assert_called_once_with(data)
    display_moved.assert_called_once_with(data)


@pytest.mark.parametrize("size", [IVector2(1), IVector2(200, 100)])
def test_change_display_size(connected_display, size):
    with (
        patch.object(Display, "resized", new=MagicMock()) as Display_resized,
        patch.object(connected_display, "resized", new=MagicMock()) as display_resized,
    ):
        change_display_size(connected_display._sdl_display, size)
    assert connected_display.bounds.size == size
    data = {"display": connected_display, "size": size}
    Display_resized.assert_called_once_with(data)
    display_resized.assert_called_once_with(data)


@pytest.mark.parametrize("refresh_rate", [0.0, 70.123454])
def test_change_display_refresh_rate(connected_display, refresh_rate):
    with (
        patch.object(
            Display, "refresh_rate_changed", new=MagicMock()
        ) as Display_refresh_rate_changed,
        patch.object(
            connected_display, "refresh_rate_changed", new=MagicMock()
        ) as display_refresh_rate_changed,
    ):
        change_display_refresh_rate(connected_display._sdl_display, refresh_rate)
    assert connected_display.refresh_rate == refresh_rate
    data = {"display": connected_display, "refresh_rate": refresh_rate}
    Display_refresh_rate_changed.assert_called_once_with(data)
    display_refresh_rate_changed.assert_called_once_with(data)


@pytest.mark.parametrize("size", [IVector2(1, 2), IVector2(1000, 2000)])
@pytest.mark.parametrize("refresh_rate", [60.1234, 34.0])
def test_display_mode_repr(size, refresh_rate):
    display_mode = DisplayMode(size, refresh_rate)
    assert repr(display_mode) == (
        f"<DisplayMode " f"{size.x!r}x{size.y}px " f"@ {refresh_rate:.1f} hertz" f">"
    )
