# eplatform
# python
from typing import get_args
from unittest.mock import MagicMock
from unittest.mock import PropertyMock
from unittest.mock import patch

# pytest
import pytest

# eevent
from eevent import Event

# emath
from emath import FMatrix4
from emath import IVector2

from eplatform import MouseButton
from eplatform import MouseButtonName


def test_attrs(mouse, window):
    assert mouse.position == IVector2(0, 0)
    mouse.position = IVector2(10, 10)
    with patch.object(
        window,
        "screen_space_to_world_space_transform",
        FMatrix4.orthographic(
            0, window.size.x * 0.5, window.size.y * 0.5, 0, -1000, 1000
        ).inverse(),
    ):
        assert mouse.world_position == IVector2(5, 5)
    assert isinstance(mouse.moved, Event)

    assert isinstance(mouse.scrolled, Event)
    assert isinstance(mouse.scrolled_vertically, Event)
    assert isinstance(mouse.scrolled_up, Event)
    assert isinstance(mouse.scrolled_down, Event)
    assert isinstance(mouse.scrolled_horizontally, Event)
    assert isinstance(mouse.scrolled_left, Event)
    assert isinstance(mouse.scrolled_right, Event)

    assert isinstance(mouse.button_changed, Event)
    assert isinstance(mouse.button_pressed, Event)
    assert isinstance(mouse.button_released, Event)

    for button_name in get_args(MouseButtonName):
        button = getattr(mouse, button_name)
        assert isinstance(button, MouseButton)
        assert button.name == button_name
        assert not button.is_pressed
        assert isinstance(button.changed, Event)
        assert isinstance(button.released, Event)
        assert isinstance(button.pressed, Event)


@pytest.mark.parametrize("position", [IVector2(0, 0), IVector2(-1, 4)])
@pytest.mark.parametrize("delta", [IVector2(2, -3), IVector2(-1, 4)])
def test_move(window, mouse, position, delta):
    world_position = object()
    with (
        patch.object(mouse, "moved", new=MagicMock()) as moved,
        patch(
            "eplatform._mouse.Mouse.world_position",
            new_callable=PropertyMock,
            return_value=world_position,
        ),
    ):
        mouse.move(position, delta)
    moved.assert_called_once_with(
        {"position": position, "delta": delta, "world_position": world_position}
    )
    assert mouse.position == position


@pytest.mark.parametrize("x", [-1, 0, 1])
@pytest.mark.parametrize("y", [-1, 0, 1])
def test_scroll(mouse, x, y):
    with (
        patch.object(mouse, "scrolled", new=MagicMock()) as scrolled,
        patch.object(mouse, "scrolled_vertically", new=MagicMock()) as scrolled_vertically,
        patch.object(mouse, "scrolled_up", new=MagicMock()) as scrolled_up,
        patch.object(mouse, "scrolled_down", new=MagicMock()) as scrolled_down,
        patch.object(mouse, "scrolled_horizontally", new=MagicMock()) as scrolled_horizontally,
        patch.object(mouse, "scrolled_left", new=MagicMock()) as scrolled_left,
        patch.object(mouse, "scrolled_right", new=MagicMock()) as scrolled_right,
    ):
        mouse.scroll(IVector2(x, y))
    scrolled.assert_called_once_with({"delta": IVector2(x, y)})
    if y:
        scrolled_vertically.assert_called_once_with({"delta": y})
        if y > 0:
            scrolled_up.assert_called_once_with({"delta": y})
        else:
            scrolled_down.assert_called_once_with({"delta": y})
    if x:
        scrolled_horizontally.assert_called_once_with({"delta": x})
        if x > 0:
            scrolled_right.assert_called_once_with({"delta": x})
        else:
            scrolled_left.assert_called_once_with({"delta": x})


@pytest.mark.parametrize("button_name", get_args(MouseButtonName))
@pytest.mark.parametrize("is_pressed", [False, True])
def test_change_button(mouse, button_name, is_pressed):
    world_position = object()
    button = getattr(mouse, button_name)
    with (
        patch.object(mouse, "button_changed", new=MagicMock()) as mouse_button_changed,
        patch.object(mouse, "button_pressed", new=MagicMock()) as mouse_button_pressed,
        patch.object(mouse, "button_released", new=MagicMock()) as mouse_button_released,
        patch.object(button, "changed", new=MagicMock()) as button_changed,
        patch.object(button, "pressed", new=MagicMock()) as button_pressed,
        patch.object(button, "released", new=MagicMock()) as button_released,
        patch(
            "eplatform._mouse.Mouse.world_position",
            new_callable=PropertyMock,
            return_value=world_position,
        ),
    ):
        mouse.change_button(button_name, is_pressed)
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


@pytest.mark.parametrize("button_name", get_args(MouseButtonName))
def test_button_repr(mouse, button_name):
    button = getattr(mouse, button_name)
    assert repr(button) == f"<MouseButton {button_name!r}>"


def test_visibility(mouse):
    mouse.show()
    mouse.hide()
    mouse.hide()
    mouse.show()
    mouse.show()
