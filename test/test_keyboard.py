# eplatform
from eplatform import Keyboard
from eplatform import KeyboardKey
from eplatform import KeyboardKeyName

# eevent
from eevent import Event

# pytest
import pytest

# python
from typing import get_args
from unittest.mock import MagicMock
from unittest.mock import patch


def test_attrs(keyboard):
    assert isinstance(keyboard, Keyboard)

    assert isinstance(keyboard.key_changed, Event)
    assert isinstance(keyboard.key_pressed, Event)
    assert isinstance(keyboard.key_released, Event)

    for key_name in get_args(KeyboardKeyName):
        key = getattr(keyboard, key_name)
        assert isinstance(key, KeyboardKey)
        assert key.name == key_name
        assert not key.is_pressed
        assert isinstance(key.changed, Event)
        assert isinstance(key.released, Event)
        assert isinstance(key.pressed, Event)


@pytest.mark.parametrize("is_pressed", [False, True])
def test_change_key(keyboard, is_pressed):
    for key_name in get_args(KeyboardKeyName):
        key = getattr(keyboard, key_name)
        with (
            patch.object(keyboard, "key_changed", new=MagicMock()) as keyboard_key_changed,
            patch.object(keyboard, "key_pressed", new=MagicMock()) as keyboard_key_pressed,
            patch.object(keyboard, "key_released", new=MagicMock()) as keyboard_key_released,
            patch.object(key, "changed", new=MagicMock()) as key_changed,
            patch.object(key, "pressed", new=MagicMock()) as key_pressed,
            patch.object(key, "released", new=MagicMock()) as key_released,
        ):
            keyboard.change_key(key_name, is_pressed)
        keyboard_key_changed.assert_called_once_with({"key": key, "is_pressed": is_pressed})
        key_changed.assert_called_once_with({"key": key, "is_pressed": is_pressed})
        if is_pressed:
            keyboard_key_pressed.assert_called_once_with({"key": key, "is_pressed": is_pressed})
            key_pressed.assert_called_once_with({"key": key, "is_pressed": is_pressed})
        else:
            keyboard_key_released.assert_called_once_with({"key": key, "is_pressed": is_pressed})
            key_released.assert_called_once_with({"key": key, "is_pressed": is_pressed})
        assert key.is_pressed == is_pressed


def test_key_repr(keyboard):
    for key_name in get_args(KeyboardKeyName):
        key = getattr(keyboard, key_name)
        assert repr(key) == f"<KeyboardKey {key_name!r}>"
