# eplatform
# python
from unittest.mock import MagicMock
from unittest.mock import patch

# pytest
import pytest

# egeometry
from egeometry import IRectangle

# emath
from emath import FMatrix4
from emath import IVector2

from eplatform import Window
from eplatform import WindowBufferSynchronization
from eplatform import WindowDestroyedError


@patch("eplatform._window.create_sdl_window")
def test_init(create_sdl_window):
    create_sdl_window.return_value = None
    window = Window()
    assert window.screen_space_to_world_space_transform == FMatrix4(1)


def test_size(window):
    assert window.size == IVector2(200, 200)

    with patch.object(window, "resized", new=MagicMock()) as window_resized:
        window.size = IVector2(100, 101)
    assert window.size == IVector2(100, 101)
    window_resized.assert_called_once_with({"size": IVector2(100, 101)})


def test_resize(window, capture_event):
    def _():
        window.resize(IVector2(100, 150))
        assert window.size == IVector2(200, 200)

    event = capture_event(_, window.resized)
    assert event == {"size": IVector2(100, 150)}
    assert window.size == IVector2(100, 150)


def test_is_visible(window):
    assert not window.is_visible

    with (
        patch.object(window, "visibility_changed", new=MagicMock()) as window_visibility_changed,
        patch.object(window, "shown", new=MagicMock()) as window_shown,
    ):
        window.is_visible = True
    assert window.is_visible
    window_visibility_changed.assert_called_once_with({"is_visible": True})
    window_shown.assert_called_once_with({"is_visible": True})

    with (
        patch.object(window, "visibility_changed", new=MagicMock()) as window_visibility_changed,
        patch.object(window, "hidden", new=MagicMock()) as window_hidden,
    ):
        window.is_visible = False
    assert not window.is_visible
    window_visibility_changed.assert_called_once_with({"is_visible": False})
    window_hidden.assert_called_once_with({"is_visible": False})


def test_show_hide(window, capture_event):
    def _():
        window.show()
        assert not window.is_visible

    event = capture_event(_, window.visibility_changed)
    assert event == {"is_visible": True}
    assert window.is_visible

    def _():
        window.hide()
        assert window.is_visible

    event = capture_event(_, window.visibility_changed)
    assert event == {"is_visible": False}
    assert not window.is_visible

    def _():
        window.show()
        assert not window.is_visible

    event = capture_event(_, window.shown)
    assert event == {"is_visible": True}
    assert window.is_visible

    def _():
        window.hide()
        assert window.is_visible

    event = capture_event(_, window.hidden)
    assert event == {"is_visible": False}
    assert not window.is_visible


def test_center(window):
    window.center()


@pytest.mark.parametrize("synchronization", list(WindowBufferSynchronization))
def test_refresh(window, synchronization: WindowBufferSynchronization) -> None:
    window.refresh(synchronization)


@pytest.mark.parametrize(
    "transform, screen_coordinate, expected_world_coordinate",
    [
        (FMatrix4.orthographic(0, 100, 100, 0, -1000, 1000).inverse(), IVector2(0), IVector2(0)),
        (
            FMatrix4.orthographic(0, 100, 100, 0, -1000, 1000).inverse(),
            IVector2(10, 20),
            IVector2(5, 10),
        ),
        (FMatrix4.orthographic(0, 200, 200, 0, -1000, 1000).inverse(), IVector2(0), IVector2(0)),
        (
            FMatrix4.orthographic(0, 200, 200, 0, -1000, 1000).inverse(),
            IVector2(10, 20),
            IVector2(10, 20),
        ),
        (FMatrix4.orthographic(0, 400, 400, 0, -1000, 1000).inverse(), IVector2(0), IVector2(0)),
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


@pytest.mark.parametrize("text", ["", "hello", "私"])
def test_input_text(window, text):
    with patch.object(window, "text_inputted", new=MagicMock()) as text_inputted:
        window.input_text(text)
    text_inputted.assert_called_once_with({"text": text})


def test_start_stop_input(window):
    rect = IRectangle(IVector2(0), IVector2(1))
    window.enable_text_input(rect)
    window.enable_text_input(rect)
    window.disable_text_input()
    window.disable_text_input()

    with window.text_input(rect):
        pass


def test_destroyed_window(window):
    window._delete_sdl_window()
    window._delete_sdl_window()
    window.close()
    with pytest.raises(WindowDestroyedError):
        window.enable_text_input(IRectangle(IVector2(0), IVector2(1)))
    window.disable_text_input()
    with pytest.raises(WindowDestroyedError):
        with window.text_input(IRectangle(IVector2(0), IVector2(1))):
            pass
    window.input_text("a")
    with pytest.raises(WindowDestroyedError):
        window.show()
    window.hide()
    with pytest.raises(WindowDestroyedError):
        window.center()
    with pytest.raises(WindowDestroyedError):
        window.refresh()
    with pytest.raises(WindowDestroyedError):
        window.resize(IVector2(100, 100))
    assert window.size
    window.size = IVector2(101, 102)
    window.convert_screen_coordinate_to_world_coordinate(IVector2(0, 0))
