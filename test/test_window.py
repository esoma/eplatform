# eplatform
from eplatform import Window
from eplatform import WindowBufferSynchronization

# emath
from emath import FMatrix4
from emath import IVector2

# pysdl2
from sdl2 import SDL_WINDOW_HIDDEN
from sdl2 import SDL_WINDOW_OPENGL
from sdl2.ext import Window as SdlWindow

# pytest
import pytest

# python
from unittest.mock import patch


@patch("eplatform._window._Window.__init__")
def test_init(super_init):
    window = Window()
    window.window = None
    super_init.assert_called_once_with("", (200, 200), flags=SDL_WINDOW_HIDDEN | SDL_WINDOW_OPENGL)
    assert window.screen_space_to_world_space_transform == FMatrix4(1)


def test_attrs(window):
    assert isinstance(window, SdlWindow)
    assert window.size == IVector2(200, 200)


@pytest.mark.parametrize("synchronization", list(WindowBufferSynchronization))
def test_refresh(window, synchronization: WindowBufferSynchronization) -> None:
    window.refresh(synchronization)


@pytest.mark.parametrize(
    "transform, screen_coordinate, expected_world_coordinate",
    [
        (
            FMatrix4.orthographic(0, 100, 100, 0, -1000, 1000).inverse(),
            IVector2(0),
            IVector2(0),
        ),
        (
            FMatrix4.orthographic(0, 100, 100, 0, -1000, 1000).inverse(),
            IVector2(10, 20),
            IVector2(5, 10),
        ),
        (
            FMatrix4.orthographic(0, 200, 200, 0, -1000, 1000).inverse(),
            IVector2(0),
            IVector2(0),
        ),
        (
            FMatrix4.orthographic(0, 200, 200, 0, -1000, 1000).inverse(),
            IVector2(10, 20),
            IVector2(10, 20),
        ),
        (
            FMatrix4.orthographic(0, 400, 400, 0, -1000, 1000).inverse(),
            IVector2(0),
            IVector2(0),
        ),
        (
            FMatrix4.orthographic(0, 400, 400, 0, -1000, 1000).inverse(),
            IVector2(10, 20),
            IVector2(20, 40),
        ),
    ],
)
def test_convert_screen_coordinate_to_world_coordinate(
    window, transform, screen_coordinate, expected_world_coordinate
):
    window.screen_space_to_world_space_transform = transform
    assert (
        window.convert_screen_coordinate_to_world_coordinate(screen_coordinate)
        == expected_world_coordinate
    )
