from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from egeometry import IRectangle
from emath import FMatrix4
from emath import IVector2

from eplatform import Window
from eplatform import WindowBufferSynchronization
from eplatform import WindowDestroyedError
from eplatform import get_displays
from eplatform._window import blur_window
from eplatform._window import close_window
from eplatform._window import delete_window
from eplatform._window import focus_window
from eplatform._window import hide_window
from eplatform._window import input_window_text
from eplatform._window import move_window
from eplatform._window import resize_window
from eplatform._window import show_window


@patch("eplatform._window.create_sdl_window")
def test_init(create_sdl_window):
    create_sdl_window.return_value = (None, 0, 0)
    window = Window()
    assert window.screen_space_to_world_space_transform == FMatrix4(1)


def test_position(window):
    assert isinstance(window.position, IVector2)

    new_position = window.position + IVector2(-1, 1)

    with patch.object(window, "moved", new=MagicMock()) as window_moved:
        move_window(window, new_position)

    assert window.position == new_position
    window_moved.assert_called_once_with({"position": new_position})


def test_close():
    window = MagicMock()
    close_window(window)
    window.closed.assert_called_once_with(None)


def test_is_focused(window):
    assert not window.is_focused

    with patch.object(window, "focused", new=MagicMock()) as window_focused:
        focus_window(window)
    assert window.is_focused
    window_focused.assert_called_once_with(None)

    with patch.object(window, "blurred", new=MagicMock()) as window_blurred:
        blur_window(window)
    assert not window.is_focused
    window_blurred.assert_called_once_with(None)


def test_is_bordered(window):
    assert window.is_bordered
    window.show_border()
    assert window.is_bordered
    window.hide_border()
    assert not window.is_bordered
    window.hide_border()
    assert not window.is_bordered
    window.show_border()
    assert window.is_bordered


def test_is_fullscreen(window):
    displays = tuple(d for d in get_displays() if d.modes)
    if len(displays) < 1:
        pytest.skip("test requires at least 1 display with fullscreen modes")
    display = displays[0]
    display_mode = display.modes[0]

    assert not window.is_fullscreen
    window.window()
    assert not window.is_fullscreen
    window.fullscreen(display, display_mode)
    assert window.is_fullscreen
    window.fullscreen(display, display_mode)
    assert window.is_fullscreen
    window.window()
    assert not window.is_fullscreen


def test_is_always_on_top(window):
    assert not window.is_always_on_top
    window.allow_not_on_top()
    assert not window.is_always_on_top
    window.force_always_on_top()
    assert window.is_always_on_top
    window.force_always_on_top()
    assert window.is_always_on_top
    window.allow_not_on_top()
    assert not window.is_always_on_top


def test_size(window):
    assert window.size == IVector2(200, 200)

    with patch.object(window, "resized", new=MagicMock()) as window_resized:
        resize_window(window, IVector2(100, 101))

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
        show_window(window)
    assert window.is_visible
    window_visibility_changed.assert_called_once_with({"is_visible": True})
    window_shown.assert_called_once_with({"is_visible": True})

    with (
        patch.object(window, "visibility_changed", new=MagicMock()) as window_visibility_changed,
        patch.object(window, "hidden", new=MagicMock()) as window_hidden,
    ):
        hide_window(window)
    assert not window.is_visible
    window_visibility_changed.assert_called_once_with({"is_visible": False})
    window_hidden.assert_called_once_with({"is_visible": False})


@pytest.mark.disruptive
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
        input_window_text(window, text)
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
    delete_window(window)
    delete_window(window)
    with pytest.raises(WindowDestroyedError):
        window.enable_text_input(IRectangle(IVector2(0), IVector2(1)))
    window.disable_text_input()
    with pytest.raises(WindowDestroyedError):
        with window.text_input(IRectangle(IVector2(0), IVector2(1))):
            pass
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
    window.convert_screen_coordinate_to_world_coordinate(IVector2(0, 0))
