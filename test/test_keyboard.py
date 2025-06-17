from typing import get_args
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from eevent import Event

from eplatform import Keyboard
from eplatform import KeyboardKey
from eplatform import KeyboardKeyLocation
from eplatform import KeyboardModifier
from eplatform import _eplatform
from eplatform._keyboard import change_key

SDL_SCANCODE_KEYBOARD_KEY_LOCATION = (
    # number
    (_eplatform.SDL_SCANCODE_0, KeyboardKeyLocation.ZERO),
    (_eplatform.SDL_SCANCODE_1, KeyboardKeyLocation.ONE),
    (_eplatform.SDL_SCANCODE_2, KeyboardKeyLocation.TWO),
    (_eplatform.SDL_SCANCODE_3, KeyboardKeyLocation.THREE),
    (_eplatform.SDL_SCANCODE_4, KeyboardKeyLocation.FOUR),
    (_eplatform.SDL_SCANCODE_5, KeyboardKeyLocation.FIVE),
    (_eplatform.SDL_SCANCODE_6, KeyboardKeyLocation.SIX),
    (_eplatform.SDL_SCANCODE_7, KeyboardKeyLocation.SEVEN),
    (_eplatform.SDL_SCANCODE_8, KeyboardKeyLocation.EIGHT),
    (_eplatform.SDL_SCANCODE_9, KeyboardKeyLocation.NINE),
    # function
    (_eplatform.SDL_SCANCODE_F1, KeyboardKeyLocation.F1),
    (_eplatform.SDL_SCANCODE_F2, KeyboardKeyLocation.F2),
    (_eplatform.SDL_SCANCODE_F3, KeyboardKeyLocation.F3),
    (_eplatform.SDL_SCANCODE_F4, KeyboardKeyLocation.F4),
    (_eplatform.SDL_SCANCODE_F5, KeyboardKeyLocation.F5),
    (_eplatform.SDL_SCANCODE_F6, KeyboardKeyLocation.F6),
    (_eplatform.SDL_SCANCODE_F7, KeyboardKeyLocation.F7),
    (_eplatform.SDL_SCANCODE_F8, KeyboardKeyLocation.F8),
    (_eplatform.SDL_SCANCODE_F9, KeyboardKeyLocation.F9),
    (_eplatform.SDL_SCANCODE_F10, KeyboardKeyLocation.F10),
    (_eplatform.SDL_SCANCODE_F11, KeyboardKeyLocation.F11),
    (_eplatform.SDL_SCANCODE_F12, KeyboardKeyLocation.F12),
    (_eplatform.SDL_SCANCODE_F13, KeyboardKeyLocation.F13),
    (_eplatform.SDL_SCANCODE_F14, KeyboardKeyLocation.F14),
    (_eplatform.SDL_SCANCODE_F15, KeyboardKeyLocation.F15),
    (_eplatform.SDL_SCANCODE_F16, KeyboardKeyLocation.F16),
    (_eplatform.SDL_SCANCODE_F17, KeyboardKeyLocation.F17),
    (_eplatform.SDL_SCANCODE_F18, KeyboardKeyLocation.F18),
    (_eplatform.SDL_SCANCODE_F19, KeyboardKeyLocation.F19),
    (_eplatform.SDL_SCANCODE_F20, KeyboardKeyLocation.F20),
    (_eplatform.SDL_SCANCODE_F21, KeyboardKeyLocation.F21),
    (_eplatform.SDL_SCANCODE_F22, KeyboardKeyLocation.F22),
    (_eplatform.SDL_SCANCODE_F23, KeyboardKeyLocation.F23),
    (_eplatform.SDL_SCANCODE_F24, KeyboardKeyLocation.F24),
    # letters
    (_eplatform.SDL_SCANCODE_A, KeyboardKeyLocation.A),
    (_eplatform.SDL_SCANCODE_B, KeyboardKeyLocation.B),
    (_eplatform.SDL_SCANCODE_C, KeyboardKeyLocation.C),
    (_eplatform.SDL_SCANCODE_D, KeyboardKeyLocation.D),
    (_eplatform.SDL_SCANCODE_E, KeyboardKeyLocation.E),
    (_eplatform.SDL_SCANCODE_F, KeyboardKeyLocation.F),
    (_eplatform.SDL_SCANCODE_G, KeyboardKeyLocation.G),
    (_eplatform.SDL_SCANCODE_H, KeyboardKeyLocation.H),
    (_eplatform.SDL_SCANCODE_I, KeyboardKeyLocation.I),
    (_eplatform.SDL_SCANCODE_J, KeyboardKeyLocation.J),
    (_eplatform.SDL_SCANCODE_K, KeyboardKeyLocation.K),
    (_eplatform.SDL_SCANCODE_L, KeyboardKeyLocation.L),
    (_eplatform.SDL_SCANCODE_M, KeyboardKeyLocation.M),
    (_eplatform.SDL_SCANCODE_N, KeyboardKeyLocation.N),
    (_eplatform.SDL_SCANCODE_O, KeyboardKeyLocation.O),
    (_eplatform.SDL_SCANCODE_P, KeyboardKeyLocation.P),
    (_eplatform.SDL_SCANCODE_Q, KeyboardKeyLocation.Q),
    (_eplatform.SDL_SCANCODE_R, KeyboardKeyLocation.R),
    (_eplatform.SDL_SCANCODE_S, KeyboardKeyLocation.S),
    (_eplatform.SDL_SCANCODE_T, KeyboardKeyLocation.T),
    (_eplatform.SDL_SCANCODE_U, KeyboardKeyLocation.U),
    (_eplatform.SDL_SCANCODE_V, KeyboardKeyLocation.V),
    (_eplatform.SDL_SCANCODE_W, KeyboardKeyLocation.W),
    (_eplatform.SDL_SCANCODE_X, KeyboardKeyLocation.X),
    (_eplatform.SDL_SCANCODE_Y, KeyboardKeyLocation.Y),
    (_eplatform.SDL_SCANCODE_Z, KeyboardKeyLocation.Z),
    # symbols/operators
    (_eplatform.SDL_SCANCODE_APOSTROPHE, KeyboardKeyLocation.APOSTROPHE),
    (_eplatform.SDL_SCANCODE_BACKSLASH, KeyboardKeyLocation.BACKSLASH),
    (_eplatform.SDL_SCANCODE_COMMA, KeyboardKeyLocation.COMMA),
    (_eplatform.SDL_SCANCODE_DECIMALSEPARATOR, KeyboardKeyLocation.DECIMAL_SEPARATOR),
    (_eplatform.SDL_SCANCODE_EQUALS, KeyboardKeyLocation.EQUALS),
    (_eplatform.SDL_SCANCODE_GRAVE, KeyboardKeyLocation.GRAVE),
    (_eplatform.SDL_SCANCODE_LEFTBRACKET, KeyboardKeyLocation.LEFT_BRACKET),
    (_eplatform.SDL_SCANCODE_MINUS, KeyboardKeyLocation.MINUS),
    (_eplatform.SDL_SCANCODE_NONUSBACKSLASH, KeyboardKeyLocation.NON_US_BACKSLASH),
    (_eplatform.SDL_SCANCODE_NONUSHASH, KeyboardKeyLocation.NON_US_HASH),
    (_eplatform.SDL_SCANCODE_PERIOD, KeyboardKeyLocation.PERIOD),
    (_eplatform.SDL_SCANCODE_RIGHTBRACKET, KeyboardKeyLocation.RIGHT_BRACKET),
    (_eplatform.SDL_SCANCODE_RSHIFT, KeyboardKeyLocation.RIGHT_SHIFT),
    (_eplatform.SDL_SCANCODE_SEMICOLON, KeyboardKeyLocation.SEMICOLON),
    (_eplatform.SDL_SCANCODE_SEPARATOR, KeyboardKeyLocation.SEPARATOR),
    (_eplatform.SDL_SCANCODE_SLASH, KeyboardKeyLocation.SLASH),
    (_eplatform.SDL_SCANCODE_SPACE, KeyboardKeyLocation.SPACE),
    (_eplatform.SDL_SCANCODE_TAB, KeyboardKeyLocation.TAB),
    (_eplatform.SDL_SCANCODE_THOUSANDSSEPARATOR, KeyboardKeyLocation.THOUSANDS_SEPARATOR),
    # actions
    (_eplatform.SDL_SCANCODE_AGAIN, KeyboardKeyLocation.AGAIN),
    (_eplatform.SDL_SCANCODE_ALTERASE, KeyboardKeyLocation.ALT_ERASE),
    (_eplatform.SDL_SCANCODE_APPLICATION, KeyboardKeyLocation.CONTEXT_MENU),
    (_eplatform.SDL_SCANCODE_BACKSPACE, KeyboardKeyLocation.BACKSPACE),
    (_eplatform.SDL_SCANCODE_CANCEL, KeyboardKeyLocation.CANCEL),
    (_eplatform.SDL_SCANCODE_CAPSLOCK, KeyboardKeyLocation.CAPSLOCK),
    (_eplatform.SDL_SCANCODE_CLEAR, KeyboardKeyLocation.CLEAR),
    (_eplatform.SDL_SCANCODE_CLEARAGAIN, KeyboardKeyLocation.CLEAR_AGAIN),
    (_eplatform.SDL_SCANCODE_COPY, KeyboardKeyLocation.COPY),
    (_eplatform.SDL_SCANCODE_CRSEL, KeyboardKeyLocation.CRSEL),
    (_eplatform.SDL_SCANCODE_CURRENCYSUBUNIT, KeyboardKeyLocation.CURRENCY_SUB_UNIT),
    (_eplatform.SDL_SCANCODE_CURRENCYUNIT, KeyboardKeyLocation.CURRENCY_UNIT),
    (_eplatform.SDL_SCANCODE_CUT, KeyboardKeyLocation.CUT),
    (_eplatform.SDL_SCANCODE_DELETE, KeyboardKeyLocation.DELETE),
    (_eplatform.SDL_SCANCODE_END, KeyboardKeyLocation.END),
    (_eplatform.SDL_SCANCODE_ESCAPE, KeyboardKeyLocation.ESCAPE),
    (_eplatform.SDL_SCANCODE_EXECUTE, KeyboardKeyLocation.EXECUTE),
    (_eplatform.SDL_SCANCODE_EXSEL, KeyboardKeyLocation.EXSEL),
    (_eplatform.SDL_SCANCODE_FIND, KeyboardKeyLocation.FIND),
    (_eplatform.SDL_SCANCODE_HELP, KeyboardKeyLocation.HELP),
    (_eplatform.SDL_SCANCODE_HOME, KeyboardKeyLocation.HOME),
    (_eplatform.SDL_SCANCODE_INSERT, KeyboardKeyLocation.INSERT),
    (_eplatform.SDL_SCANCODE_LALT, KeyboardKeyLocation.LEFT_ALT),
    (_eplatform.SDL_SCANCODE_LCTRL, KeyboardKeyLocation.LEFT_CONTROL),
    (_eplatform.SDL_SCANCODE_LGUI, KeyboardKeyLocation.LEFT_SPECIAL),
    (_eplatform.SDL_SCANCODE_LSHIFT, KeyboardKeyLocation.LEFT_SHIFT),
    (_eplatform.SDL_SCANCODE_MENU, KeyboardKeyLocation.MENU),
    (_eplatform.SDL_SCANCODE_MODE, KeyboardKeyLocation.MODE),
    (_eplatform.SDL_SCANCODE_MUTE, KeyboardKeyLocation.MUTE),
    (_eplatform.SDL_SCANCODE_NUMLOCKCLEAR, KeyboardKeyLocation.NUMLOCK_CLEAR),
    (_eplatform.SDL_SCANCODE_OPER, KeyboardKeyLocation.OPER),
    (_eplatform.SDL_SCANCODE_OUT, KeyboardKeyLocation.OUT),
    (_eplatform.SDL_SCANCODE_PAGEDOWN, KeyboardKeyLocation.PAGE_DOWN),
    (_eplatform.SDL_SCANCODE_PAGEUP, KeyboardKeyLocation.PAGE_UP),
    (_eplatform.SDL_SCANCODE_PASTE, KeyboardKeyLocation.PASTE),
    (_eplatform.SDL_SCANCODE_PAUSE, KeyboardKeyLocation.PAUSE),
    (_eplatform.SDL_SCANCODE_POWER, KeyboardKeyLocation.POWER),
    (_eplatform.SDL_SCANCODE_PRINTSCREEN, KeyboardKeyLocation.PRINT_SCREEN),
    (_eplatform.SDL_SCANCODE_PRIOR, KeyboardKeyLocation.PRIOR),
    (_eplatform.SDL_SCANCODE_RALT, KeyboardKeyLocation.RIGHT_ALT),
    (_eplatform.SDL_SCANCODE_RCTRL, KeyboardKeyLocation.RIGHT_CONTROL),
    (_eplatform.SDL_SCANCODE_RETURN, KeyboardKeyLocation.ENTER),
    (_eplatform.SDL_SCANCODE_RETURN2, KeyboardKeyLocation.ENTER_2),
    (_eplatform.SDL_SCANCODE_RGUI, KeyboardKeyLocation.RIGHT_SPECIAL),
    (_eplatform.SDL_SCANCODE_SCROLLLOCK, KeyboardKeyLocation.SCROLL_LOCK),
    (_eplatform.SDL_SCANCODE_SELECT, KeyboardKeyLocation.SELECT),
    (_eplatform.SDL_SCANCODE_SLEEP, KeyboardKeyLocation.SLEEP),
    (_eplatform.SDL_SCANCODE_STOP, KeyboardKeyLocation.STOP),
    (_eplatform.SDL_SCANCODE_SYSREQ, KeyboardKeyLocation.SYSTEM_REQUEST),
    (_eplatform.SDL_SCANCODE_UNDO, KeyboardKeyLocation.UNDO),
    (_eplatform.SDL_SCANCODE_VOLUMEDOWN, KeyboardKeyLocation.VOLUME_DOWN),
    (_eplatform.SDL_SCANCODE_VOLUMEUP, KeyboardKeyLocation.VOLUME_UP),
    # media
    (_eplatform.SDL_SCANCODE_MEDIA_EJECT, KeyboardKeyLocation.MEDIA_EJECT),
    (_eplatform.SDL_SCANCODE_MEDIA_FAST_FORWARD, KeyboardKeyLocation.MEDIA_FAST_FORWARD),
    (_eplatform.SDL_SCANCODE_MEDIA_NEXT_TRACK, KeyboardKeyLocation.MEDIA_NEXT_TRACK),
    (_eplatform.SDL_SCANCODE_MEDIA_PLAY, KeyboardKeyLocation.MEDIA_PLAY),
    (_eplatform.SDL_SCANCODE_MEDIA_PREVIOUS_TRACK, KeyboardKeyLocation.MEDIA_PREVIOUS_TRACK),
    (_eplatform.SDL_SCANCODE_MEDIA_REWIND, KeyboardKeyLocation.MEDIA_REWIND),
    (_eplatform.SDL_SCANCODE_MEDIA_SELECT, KeyboardKeyLocation.MEDIA_SELECT),
    (_eplatform.SDL_SCANCODE_MEDIA_STOP, KeyboardKeyLocation.MEDIA_STOP),
    # ac
    (_eplatform.SDL_SCANCODE_AC_BACK, KeyboardKeyLocation.AC_BACK),
    (_eplatform.SDL_SCANCODE_AC_BOOKMARKS, KeyboardKeyLocation.AC_BOOKMARKS),
    (_eplatform.SDL_SCANCODE_AC_FORWARD, KeyboardKeyLocation.AC_FORWARD),
    (_eplatform.SDL_SCANCODE_AC_HOME, KeyboardKeyLocation.AC_HOME),
    (_eplatform.SDL_SCANCODE_AC_REFRESH, KeyboardKeyLocation.AC_REFRESH),
    (_eplatform.SDL_SCANCODE_AC_SEARCH, KeyboardKeyLocation.AC_SEARCH),
    (_eplatform.SDL_SCANCODE_AC_STOP, KeyboardKeyLocation.AC_STOP),
    # arrows
    (_eplatform.SDL_SCANCODE_DOWN, KeyboardKeyLocation.DOWN),
    (_eplatform.SDL_SCANCODE_LEFT, KeyboardKeyLocation.LEFT),
    (_eplatform.SDL_SCANCODE_RIGHT, KeyboardKeyLocation.RIGHT),
    (_eplatform.SDL_SCANCODE_UP, KeyboardKeyLocation.UP),
    # international
    (_eplatform.SDL_SCANCODE_INTERNATIONAL1, KeyboardKeyLocation.INTERNATIONAL_1),
    (_eplatform.SDL_SCANCODE_INTERNATIONAL2, KeyboardKeyLocation.INTERNATIONAL_2),
    (_eplatform.SDL_SCANCODE_INTERNATIONAL3, KeyboardKeyLocation.INTERNATIONAL_3),
    (_eplatform.SDL_SCANCODE_INTERNATIONAL4, KeyboardKeyLocation.INTERNATIONAL_4),
    (_eplatform.SDL_SCANCODE_INTERNATIONAL5, KeyboardKeyLocation.INTERNATIONAL_5),
    (_eplatform.SDL_SCANCODE_INTERNATIONAL6, KeyboardKeyLocation.INTERNATIONAL_6),
    (_eplatform.SDL_SCANCODE_INTERNATIONAL7, KeyboardKeyLocation.INTERNATIONAL_7),
    (_eplatform.SDL_SCANCODE_INTERNATIONAL8, KeyboardKeyLocation.INTERNATIONAL_8),
    (_eplatform.SDL_SCANCODE_INTERNATIONAL9, KeyboardKeyLocation.INTERNATIONAL_9),
    # numpad numbers
    (_eplatform.SDL_SCANCODE_KP_0, KeyboardKeyLocation.NUMPAD_0),
    (_eplatform.SDL_SCANCODE_KP_00, KeyboardKeyLocation.NUMPAD_00),
    (_eplatform.SDL_SCANCODE_KP_000, KeyboardKeyLocation.NUMPAD_000),
    (_eplatform.SDL_SCANCODE_KP_1, KeyboardKeyLocation.NUMPAD_1),
    (_eplatform.SDL_SCANCODE_KP_2, KeyboardKeyLocation.NUMPAD_2),
    (_eplatform.SDL_SCANCODE_KP_3, KeyboardKeyLocation.NUMPAD_3),
    (_eplatform.SDL_SCANCODE_KP_4, KeyboardKeyLocation.NUMPAD_4),
    (_eplatform.SDL_SCANCODE_KP_5, KeyboardKeyLocation.NUMPAD_5),
    (_eplatform.SDL_SCANCODE_KP_6, KeyboardKeyLocation.NUMPAD_6),
    (_eplatform.SDL_SCANCODE_KP_7, KeyboardKeyLocation.NUMPAD_7),
    (_eplatform.SDL_SCANCODE_KP_8, KeyboardKeyLocation.NUMPAD_8),
    (_eplatform.SDL_SCANCODE_KP_9, KeyboardKeyLocation.NUMPAD_9),
    # numpad letters
    (_eplatform.SDL_SCANCODE_KP_A, KeyboardKeyLocation.NUMPAD_A),
    (_eplatform.SDL_SCANCODE_KP_B, KeyboardKeyLocation.NUMPAD_B),
    (_eplatform.SDL_SCANCODE_KP_C, KeyboardKeyLocation.NUMPAD_C),
    (_eplatform.SDL_SCANCODE_KP_D, KeyboardKeyLocation.NUMPAD_D),
    (_eplatform.SDL_SCANCODE_KP_E, KeyboardKeyLocation.NUMPAD_E),
    (_eplatform.SDL_SCANCODE_KP_F, KeyboardKeyLocation.NUMPAD_F),
    # numpad symbols/operators
    (_eplatform.SDL_SCANCODE_KP_AMPERSAND, KeyboardKeyLocation.NUMPAD_AMPERSAND),
    (_eplatform.SDL_SCANCODE_KP_AT, KeyboardKeyLocation.NUMPAD_AT),
    (_eplatform.SDL_SCANCODE_KP_COLON, KeyboardKeyLocation.NUMPAD_COLON),
    (_eplatform.SDL_SCANCODE_KP_COMMA, KeyboardKeyLocation.NUMPAD_COMMA),
    (_eplatform.SDL_SCANCODE_KP_DBLAMPERSAND, KeyboardKeyLocation.NUMPAD_AND),
    (_eplatform.SDL_SCANCODE_KP_DBLVERTICALBAR, KeyboardKeyLocation.NUMPAD_OR),
    (_eplatform.SDL_SCANCODE_KP_DECIMAL, KeyboardKeyLocation.NUMPAD_DECIMAL),
    (_eplatform.SDL_SCANCODE_KP_DIVIDE, KeyboardKeyLocation.NUMPAD_DIVIDE),
    (_eplatform.SDL_SCANCODE_KP_ENTER, KeyboardKeyLocation.NUMPAD_ENTER),
    (_eplatform.SDL_SCANCODE_KP_EQUALS, KeyboardKeyLocation.NUMPAD_EQUALS),
    (_eplatform.SDL_SCANCODE_KP_EQUALSAS400, KeyboardKeyLocation.NUMPAD_AS400_EQUALS),
    (_eplatform.SDL_SCANCODE_KP_EXCLAM, KeyboardKeyLocation.NUMPAD_BANG),
    (_eplatform.SDL_SCANCODE_KP_GREATER, KeyboardKeyLocation.NUMPAD_GREATER),
    (_eplatform.SDL_SCANCODE_KP_HASH, KeyboardKeyLocation.NUMPAD_HASH),
    (_eplatform.SDL_SCANCODE_KP_LEFTBRACE, KeyboardKeyLocation.NUMPAD_LEFT_BRACE),
    (_eplatform.SDL_SCANCODE_KP_LEFTPAREN, KeyboardKeyLocation.NUMPAD_LEFT_PARENTHESIS),
    (_eplatform.SDL_SCANCODE_KP_LESS, KeyboardKeyLocation.NUMPAD_LESS),
    (_eplatform.SDL_SCANCODE_KP_MINUS, KeyboardKeyLocation.NUMPAD_MINUS),
    (_eplatform.SDL_SCANCODE_KP_MULTIPLY, KeyboardKeyLocation.NUMPAD_MULTIPLY),
    (_eplatform.SDL_SCANCODE_KP_PERCENT, KeyboardKeyLocation.NUMPAD_PERCENT),
    (_eplatform.SDL_SCANCODE_KP_PERIOD, KeyboardKeyLocation.NUMPAD_PERIOD),
    (_eplatform.SDL_SCANCODE_KP_PLUS, KeyboardKeyLocation.NUMPAD_PLUS),
    (_eplatform.SDL_SCANCODE_KP_PLUSMINUS, KeyboardKeyLocation.NUMPAD_PLUS_MINUS),
    (_eplatform.SDL_SCANCODE_KP_POWER, KeyboardKeyLocation.NUMPAD_POWER),
    (_eplatform.SDL_SCANCODE_KP_RIGHTBRACE, KeyboardKeyLocation.NUMPAD_RIGHT_BRACE),
    (_eplatform.SDL_SCANCODE_KP_RIGHTPAREN, KeyboardKeyLocation.NUMPAD_RIGHT_PARENTHESIS),
    (_eplatform.SDL_SCANCODE_KP_SPACE, KeyboardKeyLocation.NUMPAD_SPACE),
    (_eplatform.SDL_SCANCODE_KP_TAB, KeyboardKeyLocation.NUMPAD_TAB),
    (_eplatform.SDL_SCANCODE_KP_VERTICALBAR, KeyboardKeyLocation.NUMPAD_PIPE),
    (_eplatform.SDL_SCANCODE_KP_XOR, KeyboardKeyLocation.NUMPAD_XOR),
    # numpad actions
    (_eplatform.SDL_SCANCODE_KP_BACKSPACE, KeyboardKeyLocation.NUMPAD_BACKSPACE),
    (_eplatform.SDL_SCANCODE_KP_BINARY, KeyboardKeyLocation.NUMPAD_BINARY),
    (_eplatform.SDL_SCANCODE_KP_CLEAR, KeyboardKeyLocation.NUMPAD_CLEAR),
    (_eplatform.SDL_SCANCODE_KP_CLEARENTRY, KeyboardKeyLocation.NUMPAD_CLEAR_ENTRY),
    (_eplatform.SDL_SCANCODE_KP_HEXADECIMAL, KeyboardKeyLocation.NUMPAD_HEXADECIMAL),
    (_eplatform.SDL_SCANCODE_KP_OCTAL, KeyboardKeyLocation.NUMPAD_OCTAL),
    # memory
    (_eplatform.SDL_SCANCODE_KP_MEMADD, KeyboardKeyLocation.NUMPAD_MEMORY_ADD),
    (_eplatform.SDL_SCANCODE_KP_MEMCLEAR, KeyboardKeyLocation.NUMPAD_MEMORY_CLEAR),
    (_eplatform.SDL_SCANCODE_KP_MEMDIVIDE, KeyboardKeyLocation.NUMPAD_MEMORY_DIVIDE),
    (_eplatform.SDL_SCANCODE_KP_MEMMULTIPLY, KeyboardKeyLocation.NUMPAD_MEMORY_MULTIPLY),
    (_eplatform.SDL_SCANCODE_KP_MEMRECALL, KeyboardKeyLocation.NUMPAD_MEMORY_RECALL),
    (_eplatform.SDL_SCANCODE_KP_MEMSTORE, KeyboardKeyLocation.NUMPAD_MEMORY_STORE),
    (_eplatform.SDL_SCANCODE_KP_MEMSUBTRACT, KeyboardKeyLocation.NUMPAD_MEMORY_SUBTRACT),
    # language
    (_eplatform.SDL_SCANCODE_LANG1, KeyboardKeyLocation.LANGUAGE_1),
    (_eplatform.SDL_SCANCODE_LANG2, KeyboardKeyLocation.LANGUAGE_2),
    (_eplatform.SDL_SCANCODE_LANG3, KeyboardKeyLocation.LANGUAGE_3),
    (_eplatform.SDL_SCANCODE_LANG4, KeyboardKeyLocation.LANGUAGE_4),
    (_eplatform.SDL_SCANCODE_LANG5, KeyboardKeyLocation.LANGUAGE_5),
    (_eplatform.SDL_SCANCODE_LANG6, KeyboardKeyLocation.LANGUAGE_6),
    (_eplatform.SDL_SCANCODE_LANG7, KeyboardKeyLocation.LANGUAGE_7),
    (_eplatform.SDL_SCANCODE_LANG8, KeyboardKeyLocation.LANGUAGE_8),
    (_eplatform.SDL_SCANCODE_LANG9, KeyboardKeyLocation.LANGUAGE_9),
)
assert len(SDL_SCANCODE_KEYBOARD_KEY_LOCATION) == len(KeyboardKeyLocation)


def test_attrs(keyboard):
    assert isinstance(keyboard, Keyboard)
    assert keyboard.modifier == KeyboardModifier.NONE

    assert isinstance(KeyboardKey.changed, Event)
    assert isinstance(KeyboardKey.pressed, Event)
    assert isinstance(KeyboardKey.released, Event)

    for key_location in KeyboardKeyLocation:
        key = keyboard.get_key_by_location(key_location)
        assert isinstance(key, KeyboardKey)
        assert key.location is key_location
        assert not key.is_pressed
        assert isinstance(key.changed, Event)
        assert isinstance(key.released, Event)
        assert isinstance(key.pressed, Event)


@pytest.mark.parametrize("is_pressed", [False, True])
@pytest.mark.parametrize("is_repeat", [False, True])
def test_change_key(keyboard, is_pressed, is_repeat):
    for sdl_scancode, key_location in SDL_SCANCODE_KEYBOARD_KEY_LOCATION:
        key = keyboard.get_key_by_location(key_location)
        with (
            patch.object(KeyboardKey, "changed", new=MagicMock()) as keyboard_key_changed,
            patch.object(KeyboardKey, "pressed", new=MagicMock()) as keyboard_key_pressed,
            patch.object(KeyboardKey, "released", new=MagicMock()) as keyboard_key_released,
            patch.object(key, "changed", new=MagicMock()) as key_changed,
            patch.object(key, "pressed", new=MagicMock()) as key_pressed,
            patch.object(key, "released", new=MagicMock()) as key_released,
        ):
            assert change_key(keyboard, sdl_scancode, is_pressed, is_repeat)

        expected_modifier = KeyboardModifier.NONE
        if is_pressed:
            if key_location in {
                KeyboardKeyLocation.LEFT_CONTROL,
                KeyboardKeyLocation.RIGHT_CONTROL,
            }:
                expected_modifier |= KeyboardModifier.CONTROL
            elif key_location in {KeyboardKeyLocation.LEFT_SHIFT, KeyboardKeyLocation.RIGHT_SHIFT}:
                expected_modifier |= KeyboardModifier.SHIFT
            elif key_location in {KeyboardKeyLocation.LEFT_ALT, KeyboardKeyLocation.RIGHT_ALT}:
                expected_modifier |= KeyboardModifier.ALT

        keyboard_key_changed.assert_called_once_with(
            {
                "key": key,
                "is_pressed": is_pressed,
                "is_repeat": is_repeat,
                "modifier": expected_modifier,
            }
        )
        key_changed.assert_called_once_with(
            {
                "key": key,
                "is_pressed": is_pressed,
                "is_repeat": is_repeat,
                "modifier": expected_modifier,
            }
        )
        if is_pressed:
            keyboard_key_pressed.assert_called_once_with(
                {
                    "key": key,
                    "is_pressed": is_pressed,
                    "is_repeat": is_repeat,
                    "modifier": expected_modifier,
                }
            )
            key_pressed.assert_called_once_with(
                {
                    "key": key,
                    "is_pressed": is_pressed,
                    "is_repeat": is_repeat,
                    "modifier": expected_modifier,
                }
            )
        else:
            keyboard_key_released.assert_called_once_with(
                {
                    "key": key,
                    "is_pressed": is_pressed,
                    "is_repeat": is_repeat,
                    "modifier": expected_modifier,
                }
            )
            key_released.assert_called_once_with(
                {
                    "key": key,
                    "is_pressed": is_pressed,
                    "is_repeat": is_repeat,
                    "modifier": expected_modifier,
                }
            )
        assert key.is_pressed == is_pressed

        change_key(keyboard, sdl_scancode, False, False)


def test_modifier(keyboard):
    assert keyboard.modifier == KeyboardModifier.NONE
    keyboard.get_key_by_location(KeyboardKeyLocation.LEFT_CONTROL).is_pressed = True
    assert keyboard.modifier == KeyboardModifier.CONTROL
    keyboard.get_key_by_location(KeyboardKeyLocation.LEFT_SHIFT).is_pressed = True
    assert keyboard.modifier == KeyboardModifier.CONTROL | KeyboardModifier.SHIFT
    keyboard.get_key_by_location(KeyboardKeyLocation.LEFT_ALT).is_pressed = True
    assert (
        keyboard.modifier
        == KeyboardModifier.CONTROL | KeyboardModifier.SHIFT | KeyboardModifier.ALT
    )
    keyboard.get_key_by_location(KeyboardKeyLocation.RIGHT_CONTROL).is_pressed = True
    assert (
        keyboard.modifier
        == KeyboardModifier.CONTROL | KeyboardModifier.SHIFT | KeyboardModifier.ALT
    )
    keyboard.get_key_by_location(KeyboardKeyLocation.RIGHT_SHIFT).is_pressed = True
    assert (
        keyboard.modifier
        == KeyboardModifier.CONTROL | KeyboardModifier.SHIFT | KeyboardModifier.ALT
    )
    keyboard.get_key_by_location(KeyboardKeyLocation.RIGHT_ALT).is_pressed = True
    assert (
        keyboard.modifier
        == KeyboardModifier.CONTROL | KeyboardModifier.SHIFT | KeyboardModifier.ALT
    )
    keyboard.get_key_by_location(KeyboardKeyLocation.LEFT_CONTROL).is_pressed = False
    assert (
        keyboard.modifier
        == KeyboardModifier.CONTROL | KeyboardModifier.SHIFT | KeyboardModifier.ALT
    )
    keyboard.get_key_by_location(KeyboardKeyLocation.LEFT_SHIFT).is_pressed = False
    assert (
        keyboard.modifier
        == KeyboardModifier.CONTROL | KeyboardModifier.SHIFT | KeyboardModifier.ALT
    )
    keyboard.get_key_by_location(KeyboardKeyLocation.LEFT_ALT).is_pressed = False
    assert (
        keyboard.modifier
        == KeyboardModifier.CONTROL | KeyboardModifier.SHIFT | KeyboardModifier.ALT
    )
    keyboard.get_key_by_location(KeyboardKeyLocation.RIGHT_CONTROL).is_pressed = False
    assert keyboard.modifier == KeyboardModifier.SHIFT | KeyboardModifier.ALT
    keyboard.get_key_by_location(KeyboardKeyLocation.RIGHT_SHIFT).is_pressed = False
    assert keyboard.modifier == KeyboardModifier.ALT
    keyboard.get_key_by_location(KeyboardKeyLocation.RIGHT_ALT).is_pressed = False
    assert keyboard.modifier == KeyboardModifier.NONE


@pytest.mark.parametrize("is_pressed", [False, True])
def test_change_key_unexpected_sdl_scancode(keyboard, is_pressed):
    with (
        patch.object(KeyboardKey, "changed", new=MagicMock()) as keyboard_key_changed,
        patch.object(KeyboardKey, "pressed", new=MagicMock()) as keyboard_key_pressed,
        patch.object(KeyboardKey, "released", new=MagicMock()) as keyboard_key_released,
    ):
        assert not change_key(keyboard, -1, is_pressed, False)
    keyboard_key_changed.assert_not_called()
    keyboard_key_pressed.assert_not_called()
    keyboard_key_released.assert_not_called()


def test_key_repr(keyboard):
    for key_location in KeyboardKeyLocation:
        key = keyboard.get_key_by_location(key_location)
        assert repr(key) == f"<KeyboardKey {key_location.value!r}>"
