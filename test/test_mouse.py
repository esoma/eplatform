from typing import get_args
from unittest.mock import MagicMock
from unittest.mock import PropertyMock
from unittest.mock import patch

import pytest
from eevent import Event
from emath import FMatrix4
from emath import IVector2

from eplatform import MouseButton
from eplatform import MouseButtonLocation
from eplatform import _eplatform
from eplatform._mouse import Mouse
from eplatform._mouse import change_mouse_button
from eplatform._mouse import change_mouse_position
from eplatform._mouse import scroll_mouse_wheel


def test_attrs(mouse, window):
    assert mouse.position == IVector2(0, 0)
    mouse._position = IVector2(10, 10)
    with patch.object(
        window,
        "screen_space_to_world_space_transform",
        FMatrix4.orthographic(
            0, window.size.x * 0.5, window.size.y * 0.5, 0, -1000, 1000
        ).inverse(),
    ):
        assert mouse.world_position == IVector2(5, 5)

    assert isinstance(Mouse.moved, Event)
    assert isinstance(mouse.moved, Event)

    assert isinstance(Mouse.scrolled, Event)
    assert isinstance(Mouse.scrolled_vertically, Event)
    assert isinstance(Mouse.scrolled_up, Event)
    assert isinstance(Mouse.scrolled_down, Event)
    assert isinstance(Mouse.scrolled_horizontally, Event)
    assert isinstance(Mouse.scrolled_left, Event)
    assert isinstance(Mouse.scrolled_right, Event)

    assert isinstance(mouse.scrolled, Event)
    assert isinstance(mouse.scrolled_vertically, Event)
    assert isinstance(mouse.scrolled_up, Event)
    assert isinstance(mouse.scrolled_down, Event)
    assert isinstance(mouse.scrolled_horizontally, Event)
    assert isinstance(mouse.scrolled_left, Event)
    assert isinstance(mouse.scrolled_right, Event)

    assert isinstance(MouseButton.changed, Event)
    assert isinstance(MouseButton.pressed, Event)
    assert isinstance(MouseButton.released, Event)

    for button_location in MouseButtonLocation:
        button = mouse.get_button(button_location)
        assert isinstance(button, MouseButton)
        assert button.location == button_location
        assert not button.is_pressed
        assert isinstance(button.changed, Event)
        assert isinstance(button.released, Event)
        assert isinstance(button.pressed, Event)


@pytest.mark.parametrize("position", [IVector2(0, 0), IVector2(-1, 4)])
@pytest.mark.parametrize("delta", [IVector2(2, -3), IVector2(-1, 4)])
def test_move(window, mouse, position, delta):
    world_position = object()
    with (
        patch.object(Mouse, "moved", new=MagicMock()) as mouse_moved,
        patch.object(mouse, "moved", new=MagicMock()) as moved,
        patch(
            "eplatform._mouse.Mouse.world_position",
            new_callable=PropertyMock,
            return_value=world_position,
        ),
    ):
        change_mouse_position(mouse, position, delta)
    mouse_moved.assert_called_once_with(
        {"position": position, "delta": delta, "world_position": world_position}
    )
    moved.assert_called_once_with(
        {"position": position, "delta": delta, "world_position": world_position}
    )
    assert mouse.position == position


@pytest.mark.parametrize("x", [-1, 0, 1])
@pytest.mark.parametrize("y", [-1, 0, 1])
def test_scroll(mouse, x, y):
    with (
        patch.object(Mouse, "scrolled", new=MagicMock()) as mouse_scrolled,
        patch.object(Mouse, "scrolled_vertically", new=MagicMock()) as mouse_scrolled_vertically,
        patch.object(Mouse, "scrolled_up", new=MagicMock()) as mouse_scrolled_up,
        patch.object(Mouse, "scrolled_down", new=MagicMock()) as mouse_scrolled_down,
        patch.object(
            Mouse, "scrolled_horizontally", new=MagicMock()
        ) as mouse_scrolled_horizontally,
        patch.object(Mouse, "scrolled_left", new=MagicMock()) as mouse_scrolled_left,
        patch.object(Mouse, "scrolled_right", new=MagicMock()) as mouse_scrolled_right,
        patch.object(mouse, "scrolled", new=MagicMock()) as scrolled,
        patch.object(mouse, "scrolled_vertically", new=MagicMock()) as scrolled_vertically,
        patch.object(mouse, "scrolled_up", new=MagicMock()) as scrolled_up,
        patch.object(mouse, "scrolled_down", new=MagicMock()) as scrolled_down,
        patch.object(mouse, "scrolled_horizontally", new=MagicMock()) as scrolled_horizontally,
        patch.object(mouse, "scrolled_left", new=MagicMock()) as scrolled_left,
        patch.object(mouse, "scrolled_right", new=MagicMock()) as scrolled_right,
    ):
        scroll_mouse_wheel(mouse, IVector2(x, y))
    mouse_scrolled.assert_called_once_with({"delta": IVector2(x, y)})
    scrolled.assert_called_once_with({"delta": IVector2(x, y)})
    if y:
        mouse_scrolled_vertically.assert_called_once_with({"delta": y})
        scrolled_vertically.assert_called_once_with({"delta": y})
        if y > 0:
            mouse_scrolled_up.assert_called_once_with({"delta": y})
            scrolled_up.assert_called_once_with({"delta": y})
        else:
            mouse_scrolled_down.assert_called_once_with({"delta": y})
            scrolled_down.assert_called_once_with({"delta": y})
    if x:
        mouse_scrolled_horizontally.assert_called_once_with({"delta": x})
        scrolled_horizontally.assert_called_once_with({"delta": x})
        if x > 0:
            mouse_scrolled_right.assert_called_once_with({"delta": x})
            scrolled_right.assert_called_once_with({"delta": x})
        else:
            mouse_scrolled_left.assert_called_once_with({"delta": x})
            scrolled_left.assert_called_once_with({"delta": x})


@pytest.mark.parametrize(
    "sdl_button, button_location",
    [
        (_eplatform.SDL_BUTTON_LEFT, MouseButtonLocation.LEFT),
        (_eplatform.SDL_BUTTON_MIDDLE, MouseButtonLocation.MIDDLE),
        (_eplatform.SDL_BUTTON_RIGHT, MouseButtonLocation.RIGHT),
        (_eplatform.SDL_BUTTON_X1, MouseButtonLocation.BACK),
        (_eplatform.SDL_BUTTON_X2, MouseButtonLocation.FORWARD),
    ],
)
@pytest.mark.parametrize("is_pressed", [False, True])
def test_change_button(mouse, sdl_button, button_location, is_pressed):
    world_position = object()
    button = mouse.get_button(button_location)
    with (
        patch.object(MouseButton, "changed", new=MagicMock()) as mouse_button_changed,
        patch.object(MouseButton, "pressed", new=MagicMock()) as mouse_button_pressed,
        patch.object(MouseButton, "released", new=MagicMock()) as mouse_button_released,
        patch.object(button, "changed", new=MagicMock()) as button_changed,
        patch.object(button, "pressed", new=MagicMock()) as button_pressed,
        patch.object(button, "released", new=MagicMock()) as button_released,
        patch(
            "eplatform._mouse.Mouse.world_position",
            new_callable=PropertyMock,
            return_value=world_position,
        ),
    ):
        change_mouse_button(mouse, sdl_button, is_pressed)
    event_data = {
        "button": button,
        "is_pressed": is_pressed,
        "position": mouse.position,
        "world_position": world_position,
    }
    mouse_button_changed.assert_called_once_with(event_data)
    button_changed.assert_called_once_with(event_data)
    if is_pressed:
        mouse_button_pressed.assert_called_once_with(event_data)
        button_pressed.assert_called_once_with(event_data)
    else:
        mouse_button_released.assert_called_once_with(event_data)
        button_released.assert_called_once_with(event_data)
    assert button.is_pressed == is_pressed


@pytest.mark.parametrize("button_location", MouseButtonLocation)
def test_button_repr(mouse, button_location):
    button = mouse.get_button(button_location)
    assert repr(button) == f"<MouseButton {button_location!r}>"


def test_visibility(mouse):
    mouse.show()
    mouse.hide()
    mouse.hide()
    mouse.show()
    mouse.show()
