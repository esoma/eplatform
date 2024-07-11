# eplatform
from eplatform._event_loop import EventLoop
from eplatform._event_loop import _Selector

# emath
from emath import IVector2

# pysdl2
import sdl2
from sdl2 import SDL_BUTTON_LEFT
from sdl2 import SDL_BUTTON_MIDDLE
from sdl2 import SDL_BUTTON_RIGHT
from sdl2 import SDL_BUTTON_X1
from sdl2 import SDL_BUTTON_X2
from sdl2 import SDL_Event
from sdl2 import SDL_KEYDOWN
from sdl2 import SDL_KEYUP
from sdl2 import SDL_MOUSEBUTTONDOWN
from sdl2 import SDL_MOUSEBUTTONUP
from sdl2 import SDL_MOUSEMOTION
from sdl2 import SDL_MOUSEWHEEL
from sdl2 import SDL_MOUSEWHEEL_FLIPPED
from sdl2 import SDL_MOUSEWHEEL_NORMAL
from sdl2 import SDL_PRESSED
from sdl2 import SDL_QUIT
from sdl2 import SDL_RELEASED

# pytest
import pytest

# python
from unittest.mock import MagicMock
from unittest.mock import patch


@patch("eplatform._event_loop.SelectorEventLoop.__init__")
def test_event_loop(super_init):
    el = EventLoop()
    el._closed = True
    super_init.assert_called_once()
    assert isinstance(super_init.call_args[0][0], _Selector)


def test_selector_select():
    selector = _Selector()
    # no events, timeout
    with (
        patch.object(selector, "_poll_sdl_events", return_value=False) as poll_sdl_events,
        patch("eplatform._event_loop.SelectSelector.select", return_value=[]) as super_select,
    ):
        assert selector.select(0.5) == []
        poll_sdl_events.assert_called_with()
        super_select.assert_called_with(0.001)
    # sdl events
    with (
        patch.object(selector, "_poll_sdl_events", return_value=True) as poll_sdl_events,
        patch("eplatform._event_loop.SelectSelector.select", return_value=[]) as super_select,
    ):
        assert selector.select() == []
        poll_sdl_events.assert_called_once_with()
        super_select.assert_called_once_with(-1)
    # select events
    with (
        patch.object(selector, "_poll_sdl_events", return_value=False) as poll_sdl_events,
        patch("eplatform._event_loop.SelectSelector.select", return_value=[True]) as super_select,
    ):
        assert selector.select() == [True]
        poll_sdl_events.assert_called_once_with()
        super_select.assert_called_once_with(0.001)


def test_selector_poll_sdl_events():
    selector = _Selector()
    selector._poll_sdl_events()

    with (
        patch("eplatform._event_loop.SDL_PollEvent", return_value=0) as sdl_poll_event,
        patch.object(selector, "_handle_sdl_event") as handle_sdl_event,
    ):
        assert not selector._poll_sdl_events()
    assert handle_sdl_event.call_count == 0
    sdl_poll_event.assert_called_once()

    ret = 1

    def _sdl_poll_event(*args, **kwargs):
        nonlocal ret
        ret -= 1
        return ret + 1

    with (
        patch(
            "eplatform._event_loop.SDL_PollEvent", side_effect=_sdl_poll_event
        ) as sdl_poll_event,
        patch.object(selector, "_handle_sdl_event") as handle_sdl_event,
    ):
        assert selector._poll_sdl_events()
    handle_sdl_event.assert_called_once()
    assert isinstance(handle_sdl_event.call_args[0][0], SDL_Event)
    assert sdl_poll_event.call_count == 2


@pytest.mark.parametrize(
    "event_type, handler_name",
    [
        (SDL_QUIT, "_handle_sdl_quit"),
        (SDL_MOUSEMOTION, "_handle_sdl_mouse_motion"),
        (SDL_MOUSEWHEEL, "_handle_sdl_mouse_wheel"),
        (SDL_MOUSEBUTTONDOWN, "_handle_sdl_mouse_button_changed"),
        (SDL_MOUSEBUTTONUP, "_handle_sdl_mouse_button_changed"),
        (SDL_KEYDOWN, "_handle_sdl_key_changed"),
        (SDL_KEYUP, "_handle_sdl_key_changed"),
    ],
)
@pytest.mark.parametrize("return_value", [False, True])
def test_selector_handle_sdl_event(event_type, handler_name, return_value):
    selector = _Selector()
    event = SDL_Event()
    event.type = event_type

    assert _Selector._SDL_EVENT_DISPATCH[event_type] is getattr(_Selector, handler_name)

    handler = MagicMock(return_value=return_value)
    with patch.dict(f"eplatform._event_loop._Selector._SDL_EVENT_DISPATCH", {event_type: handler}):
        assert selector._handle_sdl_event(event) == return_value
    handler.assert_called_once_with(selector, event)


def test_selector_handle_sdl_event_unexpected():
    selector = _Selector()
    event = SDL_Event()
    event.type = 0
    assert not selector._handle_sdl_event(event)


def test_selector_handle_sdl_quit(window):
    selector = _Selector()
    event = SDL_Event()
    event.type = SDL_QUIT

    with patch.object(window, "closed", new=MagicMock()) as closed:
        assert selector._handle_sdl_quit(event)
    closed.assert_called_once_with(None)


@pytest.mark.parametrize("x", [0, -1, 1])
@pytest.mark.parametrize("y", [0, -1, 1])
@pytest.mark.parametrize("xrel", [0, -1, 1])
@pytest.mark.parametrize("yrel", [0, -1, 1])
def test_selector_handle_sdl_mouse_motion(mouse, x, y, xrel, yrel):
    selector = _Selector()
    event = SDL_Event()
    event.type = SDL_MOUSEMOTION
    event.motion.x = x
    event.motion.y = y
    event.motion.xrel = xrel
    event.motion.yrel = yrel

    with patch.object(mouse, "move") as move:
        assert selector._handle_sdl_mouse_motion(event)
    move.assert_called_once_with(IVector2(x, y), IVector2(xrel, yrel))


@pytest.mark.parametrize("x", [0, -1, 1])
@pytest.mark.parametrize("y", [0, -1, 1])
@pytest.mark.parametrize("direction", [SDL_MOUSEWHEEL_NORMAL, SDL_MOUSEWHEEL_FLIPPED])
def test_selector_handle_sdl_mouse_wheel(mouse, x, y, direction):
    selector = _Selector()
    event = SDL_Event()
    event.type = SDL_MOUSEWHEEL
    event.wheel.x = x
    event.wheel.y = y
    event.wheel.direction = direction
    c = -1 if direction == SDL_MOUSEWHEEL_FLIPPED else 1

    with patch.object(mouse, "scroll") as scroll:
        assert selector._handle_sdl_mouse_wheel(event)
    scroll.assert_called_once_with(IVector2(x, y) * c)


@pytest.mark.parametrize(
    "sdl_button, button_name",
    [
        (SDL_BUTTON_LEFT, "left"),
        (SDL_BUTTON_MIDDLE, "middle"),
        (SDL_BUTTON_RIGHT, "right"),
        (SDL_BUTTON_X1, "back"),
        (SDL_BUTTON_X2, "forward"),
    ],
)
@pytest.mark.parametrize("is_pressed", (False, True))
@pytest.mark.parametrize("event_type", [SDL_MOUSEBUTTONDOWN, SDL_MOUSEBUTTONUP])
def test_selector_handle_sdl_mouse_button_changed(
    mouse, sdl_button, button_name, is_pressed, event_type
):
    selector = _Selector()
    event = SDL_Event()
    event.type = event_type
    event.button.button = sdl_button
    event.button.state = SDL_PRESSED if is_pressed else SDL_RELEASED

    with patch.object(mouse, "change_button") as change_button:
        assert selector._handle_sdl_mouse_button_changed(event)
    change_button.assert_called_once_with(button_name, is_pressed)


@pytest.mark.parametrize(
    "sdl_scancode, key_name",
    [
        # number
        (sdl2.SDL_SCANCODE_0, "zero"),
        (sdl2.SDL_SCANCODE_1, "one"),
        (sdl2.SDL_SCANCODE_2, "two"),
        (sdl2.SDL_SCANCODE_3, "three"),
        (sdl2.SDL_SCANCODE_4, "four"),
        (sdl2.SDL_SCANCODE_5, "five"),
        (sdl2.SDL_SCANCODE_6, "six"),
        (sdl2.SDL_SCANCODE_7, "seven"),
        (sdl2.SDL_SCANCODE_8, "eight"),
        (sdl2.SDL_SCANCODE_9, "nine"),
        # function
        (sdl2.SDL_SCANCODE_F1, "f1"),
        (sdl2.SDL_SCANCODE_F2, "f2"),
        (sdl2.SDL_SCANCODE_F3, "f3"),
        (sdl2.SDL_SCANCODE_F4, "f4"),
        (sdl2.SDL_SCANCODE_F5, "f5"),
        (sdl2.SDL_SCANCODE_F6, "f6"),
        (sdl2.SDL_SCANCODE_F7, "f7"),
        (sdl2.SDL_SCANCODE_F8, "f8"),
        (sdl2.SDL_SCANCODE_F9, "f9"),
        (sdl2.SDL_SCANCODE_F10, "f10"),
        (sdl2.SDL_SCANCODE_F11, "f11"),
        (sdl2.SDL_SCANCODE_F12, "f12"),
        (sdl2.SDL_SCANCODE_F13, "f13"),
        (sdl2.SDL_SCANCODE_F14, "f14"),
        (sdl2.SDL_SCANCODE_F15, "f15"),
        (sdl2.SDL_SCANCODE_F16, "f16"),
        (sdl2.SDL_SCANCODE_F17, "f17"),
        (sdl2.SDL_SCANCODE_F18, "f18"),
        (sdl2.SDL_SCANCODE_F19, "f19"),
        (sdl2.SDL_SCANCODE_F20, "f20"),
        (sdl2.SDL_SCANCODE_F21, "f21"),
        (sdl2.SDL_SCANCODE_F22, "f22"),
        (sdl2.SDL_SCANCODE_F23, "f23"),
        (sdl2.SDL_SCANCODE_F24, "f24"),
        # letters
        (sdl2.SDL_SCANCODE_A, "a"),
        (sdl2.SDL_SCANCODE_B, "b"),
        (sdl2.SDL_SCANCODE_C, "c"),
        (sdl2.SDL_SCANCODE_D, "d"),
        (sdl2.SDL_SCANCODE_E, "e"),
        (sdl2.SDL_SCANCODE_F, "f"),
        (sdl2.SDL_SCANCODE_G, "g"),
        (sdl2.SDL_SCANCODE_H, "h"),
        (sdl2.SDL_SCANCODE_I, "i"),
        (sdl2.SDL_SCANCODE_J, "j"),
        (sdl2.SDL_SCANCODE_K, "k"),
        (sdl2.SDL_SCANCODE_L, "l"),
        (sdl2.SDL_SCANCODE_M, "m"),
        (sdl2.SDL_SCANCODE_N, "n"),
        (sdl2.SDL_SCANCODE_O, "o"),
        (sdl2.SDL_SCANCODE_P, "p"),
        (sdl2.SDL_SCANCODE_Q, "q"),
        (sdl2.SDL_SCANCODE_R, "r"),
        (sdl2.SDL_SCANCODE_S, "s"),
        (sdl2.SDL_SCANCODE_T, "t"),
        (sdl2.SDL_SCANCODE_U, "u"),
        (sdl2.SDL_SCANCODE_V, "v"),
        (sdl2.SDL_SCANCODE_W, "w"),
        (sdl2.SDL_SCANCODE_X, "x"),
        (sdl2.SDL_SCANCODE_Y, "y"),
        (sdl2.SDL_SCANCODE_Z, "z"),
        # symbols/operators
        (sdl2.SDL_SCANCODE_APOSTROPHE, "apostrophe"),
        (sdl2.SDL_SCANCODE_BACKSLASH, "backslash"),
        (sdl2.SDL_SCANCODE_COMMA, "comma"),
        (sdl2.SDL_SCANCODE_DECIMALSEPARATOR, "decimal_separator"),
        (sdl2.SDL_SCANCODE_EQUALS, "equals"),
        (sdl2.SDL_SCANCODE_GRAVE, "grave"),
        (sdl2.SDL_SCANCODE_LEFTBRACKET, "left_bracket"),
        (sdl2.SDL_SCANCODE_MINUS, "minus"),
        (sdl2.SDL_SCANCODE_NONUSBACKSLASH, "non_us_backslash"),
        (sdl2.SDL_SCANCODE_NONUSHASH, "non_us_hash"),
        (sdl2.SDL_SCANCODE_PERIOD, "period"),
        (sdl2.SDL_SCANCODE_RIGHTBRACKET, "right_bracket"),
        (sdl2.SDL_SCANCODE_RSHIFT, "right_shift"),
        (sdl2.SDL_SCANCODE_SEMICOLON, "semicolon"),
        (sdl2.SDL_SCANCODE_SEPARATOR, "separator"),
        (sdl2.SDL_SCANCODE_SLASH, "slash"),
        (sdl2.SDL_SCANCODE_SPACE, "space"),
        (sdl2.SDL_SCANCODE_TAB, "tab"),
        (sdl2.SDL_SCANCODE_THOUSANDSSEPARATOR, "thousands_separator"),
        # actions
        (sdl2.SDL_SCANCODE_AGAIN, "again"),
        (sdl2.SDL_SCANCODE_ALTERASE, "alt_erase"),
        (sdl2.SDL_SCANCODE_APP1, "start_application_1"),
        (sdl2.SDL_SCANCODE_APP2, "start_application_2"),
        (sdl2.SDL_SCANCODE_APPLICATION, "context_menu"),
        (sdl2.SDL_SCANCODE_BACKSPACE, "backspace"),
        (sdl2.SDL_SCANCODE_BRIGHTNESSDOWN, "brightness_down"),
        (sdl2.SDL_SCANCODE_BRIGHTNESSUP, "brightness_up"),
        (sdl2.SDL_SCANCODE_CALCULATOR, "calculator"),
        (sdl2.SDL_SCANCODE_CANCEL, "cancel"),
        (sdl2.SDL_SCANCODE_CAPSLOCK, "capslock"),
        (sdl2.SDL_SCANCODE_CLEAR, "clear"),
        (sdl2.SDL_SCANCODE_CLEARAGAIN, "clear_again"),
        (sdl2.SDL_SCANCODE_COMPUTER, "computer"),
        (sdl2.SDL_SCANCODE_COPY, "copy"),
        (sdl2.SDL_SCANCODE_CRSEL, "crsel"),
        (sdl2.SDL_SCANCODE_CURRENCYSUBUNIT, "currency_sub_unit"),
        (sdl2.SDL_SCANCODE_CURRENCYUNIT, "currency_unit"),
        (sdl2.SDL_SCANCODE_CUT, "cut"),
        (sdl2.SDL_SCANCODE_DELETE, "delete"),
        (sdl2.SDL_SCANCODE_DISPLAYSWITCH, "display_switch"),
        (sdl2.SDL_SCANCODE_EJECT, "eject"),
        (sdl2.SDL_SCANCODE_END, "end"),
        (sdl2.SDL_SCANCODE_ESCAPE, "escape"),
        (sdl2.SDL_SCANCODE_EXECUTE, "execute"),
        (sdl2.SDL_SCANCODE_EXSEL, "exsel"),
        (sdl2.SDL_SCANCODE_FIND, "find"),
        (sdl2.SDL_SCANCODE_HELP, "help"),
        (sdl2.SDL_SCANCODE_HOME, "home"),
        (sdl2.SDL_SCANCODE_INSERT, "insert"),
        (sdl2.SDL_SCANCODE_KBDILLUMDOWN, "keyboard_illumination_down"),
        (sdl2.SDL_SCANCODE_KBDILLUMTOGGLE, "keyboard_illumination_toggle"),
        (sdl2.SDL_SCANCODE_KBDILLUMUP, "keyboard_illumination_up"),
        (sdl2.SDL_SCANCODE_LALT, "left_alt"),
        (sdl2.SDL_SCANCODE_LCTRL, "left_control"),
        (sdl2.SDL_SCANCODE_LGUI, "left_special"),
        (sdl2.SDL_SCANCODE_LSHIFT, "left_shift"),
        (sdl2.SDL_SCANCODE_MAIL, "mail"),
        (sdl2.SDL_SCANCODE_MEDIASELECT, "media_select"),
        (sdl2.SDL_SCANCODE_MENU, "menu"),
        (sdl2.SDL_SCANCODE_MODE, "mode"),
        (sdl2.SDL_SCANCODE_MUTE, "mute"),
        (sdl2.SDL_SCANCODE_NUMLOCKCLEAR, "numlock_clear"),
        (sdl2.SDL_SCANCODE_OPER, "oper"),
        (sdl2.SDL_SCANCODE_OUT, "out"),
        (sdl2.SDL_SCANCODE_PAGEDOWN, "page_down"),
        (sdl2.SDL_SCANCODE_PAGEUP, "page_up"),
        (sdl2.SDL_SCANCODE_PASTE, "paste"),
        (sdl2.SDL_SCANCODE_PAUSE, "pause"),
        (sdl2.SDL_SCANCODE_POWER, "power"),
        (sdl2.SDL_SCANCODE_PRINTSCREEN, "print_screen"),
        (sdl2.SDL_SCANCODE_PRIOR, "prior"),
        (sdl2.SDL_SCANCODE_RALT, "right_alt"),
        (sdl2.SDL_SCANCODE_RCTRL, "right_control"),
        (sdl2.SDL_SCANCODE_RETURN, "enter"),
        (sdl2.SDL_SCANCODE_RETURN2, "enter_2"),
        (sdl2.SDL_SCANCODE_RGUI, "right_special"),
        (sdl2.SDL_SCANCODE_SCROLLLOCK, "scroll_lock"),
        (sdl2.SDL_SCANCODE_SELECT, "select"),
        (sdl2.SDL_SCANCODE_SLEEP, "sleep"),
        (sdl2.SDL_SCANCODE_STOP, "stop"),
        (sdl2.SDL_SCANCODE_SYSREQ, "system_request"),
        (sdl2.SDL_SCANCODE_UNDO, "undo"),
        (sdl2.SDL_SCANCODE_VOLUMEDOWN, "volume_down"),
        (sdl2.SDL_SCANCODE_VOLUMEUP, "volume_up"),
        (sdl2.SDL_SCANCODE_WWW, "www"),
        # audio
        (sdl2.SDL_SCANCODE_AUDIOFASTFORWARD, "audio_fast_forward"),
        (sdl2.SDL_SCANCODE_AUDIOMUTE, "audio_mute"),
        (sdl2.SDL_SCANCODE_AUDIONEXT, "audio_next"),
        (sdl2.SDL_SCANCODE_AUDIOPLAY, "audio_play"),
        (sdl2.SDL_SCANCODE_AUDIOPREV, "audio_previous"),
        (sdl2.SDL_SCANCODE_AUDIOREWIND, "audio_rewind"),
        (sdl2.SDL_SCANCODE_AUDIOSTOP, "audio_stop"),
        # ac
        (sdl2.SDL_SCANCODE_AC_BACK, "ac_back"),
        (sdl2.SDL_SCANCODE_AC_BOOKMARKS, "ac_bookmarks"),
        (sdl2.SDL_SCANCODE_AC_FORWARD, "ac_forward"),
        (sdl2.SDL_SCANCODE_AC_HOME, "ac_home"),
        (sdl2.SDL_SCANCODE_AC_REFRESH, "ac_refresh"),
        (sdl2.SDL_SCANCODE_AC_SEARCH, "ac_search"),
        (sdl2.SDL_SCANCODE_AC_STOP, "ac_stop"),
        # arrows
        (sdl2.SDL_SCANCODE_DOWN, "down"),
        (sdl2.SDL_SCANCODE_LEFT, "left"),
        (sdl2.SDL_SCANCODE_RIGHT, "right"),
        (sdl2.SDL_SCANCODE_UP, "up"),
        # international
        (sdl2.SDL_SCANCODE_INTERNATIONAL1, "international_1"),
        (sdl2.SDL_SCANCODE_INTERNATIONAL2, "international_2"),
        (sdl2.SDL_SCANCODE_INTERNATIONAL3, "international_3"),
        (sdl2.SDL_SCANCODE_INTERNATIONAL4, "international_4"),
        (sdl2.SDL_SCANCODE_INTERNATIONAL5, "international_5"),
        (sdl2.SDL_SCANCODE_INTERNATIONAL6, "international_6"),
        (sdl2.SDL_SCANCODE_INTERNATIONAL7, "international_7"),
        (sdl2.SDL_SCANCODE_INTERNATIONAL8, "international_8"),
        (sdl2.SDL_SCANCODE_INTERNATIONAL9, "international_9"),
        # numpad numbers
        (sdl2.SDL_SCANCODE_KP_0, "numpad_0"),
        (sdl2.SDL_SCANCODE_KP_00, "numpad_00"),
        (sdl2.SDL_SCANCODE_KP_000, "numpad_000"),
        (sdl2.SDL_SCANCODE_KP_1, "numpad_1"),
        (sdl2.SDL_SCANCODE_KP_2, "numpad_2"),
        (sdl2.SDL_SCANCODE_KP_3, "numpad_3"),
        (sdl2.SDL_SCANCODE_KP_4, "numpad_4"),
        (sdl2.SDL_SCANCODE_KP_5, "numpad_5"),
        (sdl2.SDL_SCANCODE_KP_6, "numpad_6"),
        (sdl2.SDL_SCANCODE_KP_7, "numpad_7"),
        (sdl2.SDL_SCANCODE_KP_8, "numpad_8"),
        (sdl2.SDL_SCANCODE_KP_9, "numpad_9"),
        # numpad letters
        (sdl2.SDL_SCANCODE_KP_A, "numpad_a"),
        (sdl2.SDL_SCANCODE_KP_B, "numpad_b"),
        (sdl2.SDL_SCANCODE_KP_C, "numpad_c"),
        (sdl2.SDL_SCANCODE_KP_D, "numpad_d"),
        (sdl2.SDL_SCANCODE_KP_E, "numpad_e"),
        (sdl2.SDL_SCANCODE_KP_F, "numpad_f"),
        # numpad symbols/operators
        (sdl2.SDL_SCANCODE_KP_AMPERSAND, "numpad_ampersand"),
        (sdl2.SDL_SCANCODE_KP_AT, "numpad_at"),
        (sdl2.SDL_SCANCODE_KP_COLON, "numpad_colon"),
        (sdl2.SDL_SCANCODE_KP_COMMA, "numpad_comma"),
        (sdl2.SDL_SCANCODE_KP_DBLAMPERSAND, "numpad_and"),
        (sdl2.SDL_SCANCODE_KP_DBLVERTICALBAR, "numpad_or"),
        (sdl2.SDL_SCANCODE_KP_DECIMAL, "numpad_decimal"),
        (sdl2.SDL_SCANCODE_KP_DIVIDE, "numpad_divide"),
        (sdl2.SDL_SCANCODE_KP_ENTER, "numpad_enter"),
        (sdl2.SDL_SCANCODE_KP_EQUALS, "numpad_equals"),
        (sdl2.SDL_SCANCODE_KP_EQUALSAS400, "numpad_as400_equals"),
        (sdl2.SDL_SCANCODE_KP_EXCLAM, "numpad_bang"),
        (sdl2.SDL_SCANCODE_KP_GREATER, "numpad_greater"),
        (sdl2.SDL_SCANCODE_KP_HASH, "numpad_hash"),
        (sdl2.SDL_SCANCODE_KP_LEFTBRACE, "numpad_left_brace"),
        (sdl2.SDL_SCANCODE_KP_LEFTPAREN, "numpad_left_parenthesis"),
        (sdl2.SDL_SCANCODE_KP_LESS, "numpad_less"),
        (sdl2.SDL_SCANCODE_KP_MINUS, "numpad_minus"),
        (sdl2.SDL_SCANCODE_KP_MULTIPLY, "numpad_multiply"),
        (sdl2.SDL_SCANCODE_KP_PERCENT, "numpad_percent"),
        (sdl2.SDL_SCANCODE_KP_PERIOD, "numpad_period"),
        (sdl2.SDL_SCANCODE_KP_PLUS, "numpad_plus"),
        (sdl2.SDL_SCANCODE_KP_PLUSMINUS, "numpad_plus_minus"),
        (sdl2.SDL_SCANCODE_KP_POWER, "numpad_power"),
        (sdl2.SDL_SCANCODE_KP_RIGHTBRACE, "numpad_right_brace"),
        (sdl2.SDL_SCANCODE_KP_RIGHTPAREN, "numpad_right_parenthesis"),
        (sdl2.SDL_SCANCODE_KP_SPACE, "numpad_space"),
        (sdl2.SDL_SCANCODE_KP_TAB, "numpad_tab"),
        (sdl2.SDL_SCANCODE_KP_VERTICALBAR, "numpad_pipe"),
        (sdl2.SDL_SCANCODE_KP_XOR, "numpad_xor"),
        # numpad actions
        (sdl2.SDL_SCANCODE_KP_BACKSPACE, "numpad_backspace"),
        (sdl2.SDL_SCANCODE_KP_BINARY, "numpad_binary"),
        (sdl2.SDL_SCANCODE_KP_CLEAR, "numpad_clear"),
        (sdl2.SDL_SCANCODE_KP_CLEARENTRY, "numpad_clear_entry"),
        (sdl2.SDL_SCANCODE_KP_HEXADECIMAL, "numpad_hexadecimal"),
        (sdl2.SDL_SCANCODE_KP_OCTAL, "numpad_octal"),
        # memory
        (sdl2.SDL_SCANCODE_KP_MEMADD, "numpad_memory_add"),
        (sdl2.SDL_SCANCODE_KP_MEMCLEAR, "numpad_memory_clear"),
        (sdl2.SDL_SCANCODE_KP_MEMDIVIDE, "numpad_memory_divide"),
        (sdl2.SDL_SCANCODE_KP_MEMMULTIPLY, "numpad_memory_multiply"),
        (sdl2.SDL_SCANCODE_KP_MEMRECALL, "numpad_memory_recall"),
        (sdl2.SDL_SCANCODE_KP_MEMSTORE, "numpad_memory_store"),
        (sdl2.SDL_SCANCODE_KP_MEMSUBTRACT, "numpad_memory_subtract"),
        # language
        (sdl2.SDL_SCANCODE_LANG1, "language_1"),
        (sdl2.SDL_SCANCODE_LANG2, "language_2"),
        (sdl2.SDL_SCANCODE_LANG3, "language_3"),
        (sdl2.SDL_SCANCODE_LANG4, "language_4"),
        (sdl2.SDL_SCANCODE_LANG5, "language_5"),
        (sdl2.SDL_SCANCODE_LANG6, "language_6"),
        (sdl2.SDL_SCANCODE_LANG7, "language_7"),
        (sdl2.SDL_SCANCODE_LANG8, "language_8"),
        (sdl2.SDL_SCANCODE_LANG9, "language_9"),
    ],
)
@pytest.mark.parametrize("is_pressed", (False, True))
@pytest.mark.parametrize("event_type", [SDL_KEYDOWN, SDL_KEYUP])
@pytest.mark.parametrize("repeat", [0, 1])
def test_selector_handle_sdl_key_changed(
    keyboard, sdl_scancode, key_name, is_pressed, event_type, repeat
):
    selector = _Selector()
    event = SDL_Event()
    event.type = event_type
    event.key.keysym.scancode = sdl_scancode
    event.key.state = SDL_PRESSED if is_pressed else SDL_RELEASED
    event.key.repeat = repeat

    with patch.object(keyboard, "change_key") as change_key:
        assert selector._handle_sdl_key_changed(event) == (repeat == 0)
    if repeat == 0:
        change_key.assert_called_once_with(key_name, is_pressed)
    else:
        assert not change_key.called


@pytest.mark.parametrize("is_pressed", (False, True))
@pytest.mark.parametrize("event_type", [SDL_KEYDOWN, SDL_KEYUP])
def test_selector_handle_sdl_key_changed_unexpected(keyboard, is_pressed, event_type):
    selector = _Selector()
    event = SDL_Event()
    event.type = event_type
    event.key.keysym.scancode = 0
    event.key.state = SDL_PRESSED if is_pressed else SDL_RELEASED

    with patch.object(keyboard, "change_key") as change_key:
        assert not selector._handle_sdl_key_changed(event)
    change_key.assert_not_called()
