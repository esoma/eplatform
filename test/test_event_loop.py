# eplatform
# python
from unittest.mock import MagicMock
from unittest.mock import patch

# pytest
import pytest

# emath
from emath import IVector2

from eplatform import EventLoop
from eplatform import _eplatform
from eplatform._eplatform import clear_sdl_events
from eplatform._eplatform import push_sdl_event
from eplatform._event_loop import _Selector


@pytest.fixture
def mock_keyboard():
    keyboard = MagicMock()
    with patch("eplatform._event_loop.get_keyboard", return_value=keyboard):
        yield keyboard


@pytest.fixture
def mock_mouse():
    mouse = MagicMock()
    with patch("eplatform._event_loop.get_mouse", return_value=mouse):
        yield mouse


@pytest.fixture
def mock_window():
    window = MagicMock()
    with patch("eplatform._event_loop.get_window", return_value=window):
        yield window


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


def test_selector_poll_sdl_events_no_platform():
    selector = _Selector()
    selector._poll_sdl_events()

    clear_sdl_events()
    with patch.object(selector, "_handle_sdl_event") as handle_sdl_event:
        assert not selector._poll_sdl_events()
    assert handle_sdl_event.call_count == 0


def test_selector_poll_sdl_events_none(platform):
    selector = _Selector()
    selector._poll_sdl_events()

    clear_sdl_events()
    with patch.object(selector, "_handle_sdl_event") as handle_sdl_event:
        assert not selector._poll_sdl_events()
    assert handle_sdl_event.call_count == 0


@pytest.mark.parametrize("event_type", [_eplatform.SDL_EVENT_QUIT])
def test_selector_poll_sdl_events_default(platform, event_type):
    selector = _Selector()
    selector._poll_sdl_events()

    clear_sdl_events()
    push_sdl_event(event_type)
    with patch.object(selector, "_handle_sdl_event") as handle_sdl_event:
        assert selector._poll_sdl_events()
    handle_sdl_event.assert_called_once_with(event_type)


@pytest.mark.parametrize("event_type", [_eplatform.SDL_EVENT_MOUSE_MOTION])
@pytest.mark.parametrize("position", [IVector2(0, 1), IVector2(99, 75)])
@pytest.mark.parametrize("delta", [IVector2(1, 2), IVector2(-1, -2)])
def test_selector_poll_sdl_events_mouse_motion(platform, event_type, position, delta):
    selector = _Selector()
    selector._poll_sdl_events()

    clear_sdl_events()
    push_sdl_event(event_type, *position, *delta)
    with patch.object(selector, "_handle_sdl_event") as handle_sdl_event:
        assert selector._poll_sdl_events()
    handle_sdl_event.assert_called_once_with(event_type, position, delta)


@pytest.mark.parametrize("event_type", [_eplatform.SDL_EVENT_MOUSE_WHEEL])
@pytest.mark.parametrize("flipped", [False, True])
@pytest.mark.parametrize(
    "delta", [IVector2(1, 2), IVector2(-1, -2), IVector2(0, 1), IVector2(1, 0)]
)
def test_selector_poll_sdl_events_mouse_wheel(platform, event_type, flipped, delta):
    selector = _Selector()
    selector._poll_sdl_events()

    clear_sdl_events()
    push_sdl_event(event_type, flipped, *delta)
    with patch.object(selector, "_handle_sdl_event") as handle_sdl_event:
        assert selector._poll_sdl_events()
    handle_sdl_event.assert_called_once_with(event_type, delta * (-1 if flipped else 1))


@pytest.mark.parametrize(
    "event_type", [_eplatform.SDL_EVENT_MOUSE_BUTTON_DOWN, _eplatform.SDL_EVENT_MOUSE_BUTTON_UP]
)
@pytest.mark.parametrize("button", [0, 1, 100])
@pytest.mark.parametrize("is_pressed", [False, True])
def test_selector_poll_sdl_events_mouse_button(platform, event_type, button, is_pressed):
    selector = _Selector()
    selector._poll_sdl_events()

    clear_sdl_events()
    push_sdl_event(event_type, button, is_pressed)
    with patch.object(selector, "_handle_sdl_event") as handle_sdl_event:
        assert selector._poll_sdl_events()
    handle_sdl_event.assert_called_once_with(event_type, button, is_pressed)


@pytest.mark.parametrize(
    "event_type", [_eplatform.SDL_EVENT_KEY_DOWN, _eplatform.SDL_EVENT_KEY_UP]
)
@pytest.mark.parametrize("scancode", [0, 1, 100, 999999])
@pytest.mark.parametrize("is_pressed", [False, True])
@pytest.mark.parametrize("is_repeat", [False, True])
def test_selector_poll_sdl_events_key(platform, event_type, scancode, is_pressed, is_repeat):
    selector = _Selector()
    selector._poll_sdl_events()

    clear_sdl_events()
    push_sdl_event(event_type, scancode, is_pressed, is_repeat)
    with patch.object(selector, "_handle_sdl_event") as handle_sdl_event:
        assert selector._poll_sdl_events()
    handle_sdl_event.assert_called_once_with(event_type, scancode, is_pressed, is_repeat)


@pytest.mark.parametrize("event_type", [_eplatform.SDL_EVENT_TEXT_INPUT])
@pytest.mark.parametrize("text", ["a", "hello world"])
def test_selector_poll_sdl_events_text_input(platform, event_type, text):
    selector = _Selector()
    selector._poll_sdl_events()

    clear_sdl_events()
    push_sdl_event(event_type, text)
    with patch.object(selector, "_handle_sdl_event") as handle_sdl_event:
        assert selector._poll_sdl_events()
    handle_sdl_event.assert_called_once_with(event_type, text)


@pytest.mark.parametrize("event_type", [_eplatform.SDL_EVENT_WINDOW_RESIZED])
@pytest.mark.parametrize("size", [IVector2(2, 1), IVector2(99, 75)])
def test_selector_poll_sdl_events_window_resized(platform, event_type, size):
    selector = _Selector()
    selector._poll_sdl_events()

    clear_sdl_events()
    push_sdl_event(event_type, size.x, size.y)
    with patch.object(selector, "_handle_sdl_event") as handle_sdl_event:
        assert selector._poll_sdl_events()
    handle_sdl_event.assert_called_once_with(event_type, size)


@pytest.mark.parametrize(
    "event_type, handler_name",
    [
        (_eplatform.SDL_EVENT_QUIT, "_handle_sdl_event_quit"),
        (_eplatform.SDL_EVENT_MOUSE_MOTION, "_handle_sdl_event_mouse_motion"),
        (_eplatform.SDL_EVENT_MOUSE_WHEEL, "_handle_sdl_event_mouse_wheel"),
        (_eplatform.SDL_EVENT_MOUSE_BUTTON_DOWN, "_handle_sdl_event_mouse_button_changed"),
        (_eplatform.SDL_EVENT_MOUSE_BUTTON_UP, "_handle_sdl_event_mouse_button_changed"),
        (_eplatform.SDL_EVENT_KEY_DOWN, "_handle_sdl_event_key_changed"),
        (_eplatform.SDL_EVENT_KEY_UP, "_handle_sdl_event_key_changed"),
        (_eplatform.SDL_EVENT_TEXT_INPUT, "_handle_sdl_event_text_input"),
        (_eplatform.SDL_EVENT_WINDOW_RESIZED, "_handle_sdl_event_window_resized"),
        (_eplatform.SDL_EVENT_WINDOW_SHOWN, "_handle_sdl_event_window_shown"),
        (_eplatform.SDL_EVENT_WINDOW_HIDDEN, "_handle_sdl_event_window_hidden"),
    ],
)
@pytest.mark.parametrize("return_value", [False, True])
@pytest.mark.parametrize("args", [[], [0], [1, 2, 3, 4]])
def test_selector_handle_sdl_event(event_type, handler_name, args, return_value):
    selector = _Selector()
    assert _Selector._SDL_EVENT_DISPATCH[event_type] is getattr(_Selector, handler_name)

    handler = MagicMock(return_value=return_value)
    with patch.dict(f"eplatform._event_loop._Selector._SDL_EVENT_DISPATCH", {event_type: handler}):
        assert selector._handle_sdl_event(event_type, *args) == return_value
    handler.assert_called_once_with(selector, *args)


def test_selector_handle_sdl_event_unexpected():
    selector = _Selector()
    assert not selector._handle_sdl_event(0)


def test_selector_handle_sdl_event_quit(mock_window):
    selector = _Selector()
    assert selector._handle_sdl_event_quit()
    mock_window.close.assert_called_once()


@pytest.mark.parametrize("x", [0, -1, 1])
@pytest.mark.parametrize("y", [0, -1, 1])
@pytest.mark.parametrize("xrel", [0, -1, 1])
@pytest.mark.parametrize("yrel", [0, -1, 1])
def test_selector_handle_sdl_event_mouse_motion(mock_mouse, x, y, xrel, yrel):
    selector = _Selector()
    position = IVector2(x, y)
    delta = IVector2(xrel, yrel)
    assert selector._handle_sdl_event_mouse_motion(position, delta)
    mock_mouse.move.assert_called_once_with(position, delta)


@pytest.mark.parametrize("x", [0, -1, 1])
@pytest.mark.parametrize("y", [0, -1, 1])
def test_selector_handle_sdl_event_mouse_wheel(mock_mouse, x, y):
    selector = _Selector()
    delta = IVector2(x, y)
    assert selector._handle_sdl_event_mouse_wheel(delta)
    mock_mouse.scroll.assert_called_once_with(delta)


@pytest.mark.parametrize(
    "sdl_button, button_name",
    [
        (_eplatform.SDL_BUTTON_LEFT, "left"),
        (_eplatform.SDL_BUTTON_MIDDLE, "middle"),
        (_eplatform.SDL_BUTTON_RIGHT, "right"),
        (_eplatform.SDL_BUTTON_X1, "back"),
        (_eplatform.SDL_BUTTON_X2, "forward"),
    ],
)
@pytest.mark.parametrize("is_pressed", (False, True))
def test_selector_handle_sdl_mouse_button_changed(mock_mouse, sdl_button, button_name, is_pressed):
    selector = _Selector()
    assert selector._handle_sdl_event_mouse_button_changed(sdl_button, is_pressed)
    mock_mouse.change_button.assert_called_once_with(button_name, is_pressed)


@pytest.mark.parametrize(
    "sdl_scancode, key_name",
    [
        # number
        (_eplatform.SDL_SCANCODE_0, "zero"),
        (_eplatform.SDL_SCANCODE_1, "one"),
        (_eplatform.SDL_SCANCODE_2, "two"),
        (_eplatform.SDL_SCANCODE_3, "three"),
        (_eplatform.SDL_SCANCODE_4, "four"),
        (_eplatform.SDL_SCANCODE_5, "five"),
        (_eplatform.SDL_SCANCODE_6, "six"),
        (_eplatform.SDL_SCANCODE_7, "seven"),
        (_eplatform.SDL_SCANCODE_8, "eight"),
        (_eplatform.SDL_SCANCODE_9, "nine"),
        # function
        (_eplatform.SDL_SCANCODE_F1, "f1"),
        (_eplatform.SDL_SCANCODE_F2, "f2"),
        (_eplatform.SDL_SCANCODE_F3, "f3"),
        (_eplatform.SDL_SCANCODE_F4, "f4"),
        (_eplatform.SDL_SCANCODE_F5, "f5"),
        (_eplatform.SDL_SCANCODE_F6, "f6"),
        (_eplatform.SDL_SCANCODE_F7, "f7"),
        (_eplatform.SDL_SCANCODE_F8, "f8"),
        (_eplatform.SDL_SCANCODE_F9, "f9"),
        (_eplatform.SDL_SCANCODE_F10, "f10"),
        (_eplatform.SDL_SCANCODE_F11, "f11"),
        (_eplatform.SDL_SCANCODE_F12, "f12"),
        (_eplatform.SDL_SCANCODE_F13, "f13"),
        (_eplatform.SDL_SCANCODE_F14, "f14"),
        (_eplatform.SDL_SCANCODE_F15, "f15"),
        (_eplatform.SDL_SCANCODE_F16, "f16"),
        (_eplatform.SDL_SCANCODE_F17, "f17"),
        (_eplatform.SDL_SCANCODE_F18, "f18"),
        (_eplatform.SDL_SCANCODE_F19, "f19"),
        (_eplatform.SDL_SCANCODE_F20, "f20"),
        (_eplatform.SDL_SCANCODE_F21, "f21"),
        (_eplatform.SDL_SCANCODE_F22, "f22"),
        (_eplatform.SDL_SCANCODE_F23, "f23"),
        (_eplatform.SDL_SCANCODE_F24, "f24"),
        # letters
        (_eplatform.SDL_SCANCODE_A, "a"),
        (_eplatform.SDL_SCANCODE_B, "b"),
        (_eplatform.SDL_SCANCODE_C, "c"),
        (_eplatform.SDL_SCANCODE_D, "d"),
        (_eplatform.SDL_SCANCODE_E, "e"),
        (_eplatform.SDL_SCANCODE_F, "f"),
        (_eplatform.SDL_SCANCODE_G, "g"),
        (_eplatform.SDL_SCANCODE_H, "h"),
        (_eplatform.SDL_SCANCODE_I, "i"),
        (_eplatform.SDL_SCANCODE_J, "j"),
        (_eplatform.SDL_SCANCODE_K, "k"),
        (_eplatform.SDL_SCANCODE_L, "l"),
        (_eplatform.SDL_SCANCODE_M, "m"),
        (_eplatform.SDL_SCANCODE_N, "n"),
        (_eplatform.SDL_SCANCODE_O, "o"),
        (_eplatform.SDL_SCANCODE_P, "p"),
        (_eplatform.SDL_SCANCODE_Q, "q"),
        (_eplatform.SDL_SCANCODE_R, "r"),
        (_eplatform.SDL_SCANCODE_S, "s"),
        (_eplatform.SDL_SCANCODE_T, "t"),
        (_eplatform.SDL_SCANCODE_U, "u"),
        (_eplatform.SDL_SCANCODE_V, "v"),
        (_eplatform.SDL_SCANCODE_W, "w"),
        (_eplatform.SDL_SCANCODE_X, "x"),
        (_eplatform.SDL_SCANCODE_Y, "y"),
        (_eplatform.SDL_SCANCODE_Z, "z"),
        # symbols/operators
        (_eplatform.SDL_SCANCODE_APOSTROPHE, "apostrophe"),
        (_eplatform.SDL_SCANCODE_BACKSLASH, "backslash"),
        (_eplatform.SDL_SCANCODE_COMMA, "comma"),
        (_eplatform.SDL_SCANCODE_DECIMALSEPARATOR, "decimal_separator"),
        (_eplatform.SDL_SCANCODE_EQUALS, "equals"),
        (_eplatform.SDL_SCANCODE_GRAVE, "grave"),
        (_eplatform.SDL_SCANCODE_LEFTBRACKET, "left_bracket"),
        (_eplatform.SDL_SCANCODE_MINUS, "minus"),
        (_eplatform.SDL_SCANCODE_NONUSBACKSLASH, "non_us_backslash"),
        (_eplatform.SDL_SCANCODE_NONUSHASH, "non_us_hash"),
        (_eplatform.SDL_SCANCODE_PERIOD, "period"),
        (_eplatform.SDL_SCANCODE_RIGHTBRACKET, "right_bracket"),
        (_eplatform.SDL_SCANCODE_RSHIFT, "right_shift"),
        (_eplatform.SDL_SCANCODE_SEMICOLON, "semicolon"),
        (_eplatform.SDL_SCANCODE_SEPARATOR, "separator"),
        (_eplatform.SDL_SCANCODE_SLASH, "slash"),
        (_eplatform.SDL_SCANCODE_SPACE, "space"),
        (_eplatform.SDL_SCANCODE_TAB, "tab"),
        (_eplatform.SDL_SCANCODE_THOUSANDSSEPARATOR, "thousands_separator"),
        # actions
        (_eplatform.SDL_SCANCODE_AGAIN, "again"),
        (_eplatform.SDL_SCANCODE_ALTERASE, "alt_erase"),
        (_eplatform.SDL_SCANCODE_APPLICATION, "context_menu"),
        (_eplatform.SDL_SCANCODE_BACKSPACE, "backspace"),
        (_eplatform.SDL_SCANCODE_CANCEL, "cancel"),
        (_eplatform.SDL_SCANCODE_CAPSLOCK, "capslock"),
        (_eplatform.SDL_SCANCODE_CLEAR, "clear"),
        (_eplatform.SDL_SCANCODE_CLEARAGAIN, "clear_again"),
        (_eplatform.SDL_SCANCODE_COPY, "copy"),
        (_eplatform.SDL_SCANCODE_CRSEL, "crsel"),
        (_eplatform.SDL_SCANCODE_CURRENCYSUBUNIT, "currency_sub_unit"),
        (_eplatform.SDL_SCANCODE_CURRENCYUNIT, "currency_unit"),
        (_eplatform.SDL_SCANCODE_CUT, "cut"),
        (_eplatform.SDL_SCANCODE_DELETE, "delete"),
        (_eplatform.SDL_SCANCODE_END, "end"),
        (_eplatform.SDL_SCANCODE_ESCAPE, "escape"),
        (_eplatform.SDL_SCANCODE_EXECUTE, "execute"),
        (_eplatform.SDL_SCANCODE_EXSEL, "exsel"),
        (_eplatform.SDL_SCANCODE_FIND, "find"),
        (_eplatform.SDL_SCANCODE_HELP, "help"),
        (_eplatform.SDL_SCANCODE_HOME, "home"),
        (_eplatform.SDL_SCANCODE_INSERT, "insert"),
        (_eplatform.SDL_SCANCODE_LALT, "left_alt"),
        (_eplatform.SDL_SCANCODE_LCTRL, "left_control"),
        (_eplatform.SDL_SCANCODE_LGUI, "left_special"),
        (_eplatform.SDL_SCANCODE_LSHIFT, "left_shift"),
        (_eplatform.SDL_SCANCODE_MENU, "menu"),
        (_eplatform.SDL_SCANCODE_MODE, "mode"),
        (_eplatform.SDL_SCANCODE_MUTE, "mute"),
        (_eplatform.SDL_SCANCODE_NUMLOCKCLEAR, "numlock_clear"),
        (_eplatform.SDL_SCANCODE_OPER, "oper"),
        (_eplatform.SDL_SCANCODE_OUT, "out"),
        (_eplatform.SDL_SCANCODE_PAGEDOWN, "page_down"),
        (_eplatform.SDL_SCANCODE_PAGEUP, "page_up"),
        (_eplatform.SDL_SCANCODE_PASTE, "paste"),
        (_eplatform.SDL_SCANCODE_PAUSE, "pause"),
        (_eplatform.SDL_SCANCODE_POWER, "power"),
        (_eplatform.SDL_SCANCODE_PRINTSCREEN, "print_screen"),
        (_eplatform.SDL_SCANCODE_PRIOR, "prior"),
        (_eplatform.SDL_SCANCODE_RALT, "right_alt"),
        (_eplatform.SDL_SCANCODE_RCTRL, "right_control"),
        (_eplatform.SDL_SCANCODE_RETURN, "enter"),
        (_eplatform.SDL_SCANCODE_RETURN2, "enter_2"),
        (_eplatform.SDL_SCANCODE_RGUI, "right_special"),
        (_eplatform.SDL_SCANCODE_SCROLLLOCK, "scroll_lock"),
        (_eplatform.SDL_SCANCODE_SELECT, "select"),
        (_eplatform.SDL_SCANCODE_SLEEP, "sleep"),
        (_eplatform.SDL_SCANCODE_STOP, "stop"),
        (_eplatform.SDL_SCANCODE_SYSREQ, "system_request"),
        (_eplatform.SDL_SCANCODE_UNDO, "undo"),
        (_eplatform.SDL_SCANCODE_VOLUMEDOWN, "volume_down"),
        (_eplatform.SDL_SCANCODE_VOLUMEUP, "volume_up"),
        # media
        (_eplatform.SDL_SCANCODE_MEDIA_EJECT, "media_eject"),
        (_eplatform.SDL_SCANCODE_MEDIA_FAST_FORWARD, "media_fast_forward"),
        (_eplatform.SDL_SCANCODE_MEDIA_NEXT_TRACK, "media_next_track"),
        (_eplatform.SDL_SCANCODE_MEDIA_PLAY, "media_play"),
        (_eplatform.SDL_SCANCODE_MEDIA_PREVIOUS_TRACK, "media_previous_track"),
        (_eplatform.SDL_SCANCODE_MEDIA_REWIND, "media_rewind"),
        (_eplatform.SDL_SCANCODE_MEDIA_SELECT, "media_select"),
        (_eplatform.SDL_SCANCODE_MEDIA_STOP, "media_stop"),
        # ac
        (_eplatform.SDL_SCANCODE_AC_BACK, "ac_back"),
        (_eplatform.SDL_SCANCODE_AC_BOOKMARKS, "ac_bookmarks"),
        (_eplatform.SDL_SCANCODE_AC_FORWARD, "ac_forward"),
        (_eplatform.SDL_SCANCODE_AC_HOME, "ac_home"),
        (_eplatform.SDL_SCANCODE_AC_REFRESH, "ac_refresh"),
        (_eplatform.SDL_SCANCODE_AC_SEARCH, "ac_search"),
        (_eplatform.SDL_SCANCODE_AC_STOP, "ac_stop"),
        # arrows
        (_eplatform.SDL_SCANCODE_DOWN, "down"),
        (_eplatform.SDL_SCANCODE_LEFT, "left"),
        (_eplatform.SDL_SCANCODE_RIGHT, "right"),
        (_eplatform.SDL_SCANCODE_UP, "up"),
        # international
        (_eplatform.SDL_SCANCODE_INTERNATIONAL1, "international_1"),
        (_eplatform.SDL_SCANCODE_INTERNATIONAL2, "international_2"),
        (_eplatform.SDL_SCANCODE_INTERNATIONAL3, "international_3"),
        (_eplatform.SDL_SCANCODE_INTERNATIONAL4, "international_4"),
        (_eplatform.SDL_SCANCODE_INTERNATIONAL5, "international_5"),
        (_eplatform.SDL_SCANCODE_INTERNATIONAL6, "international_6"),
        (_eplatform.SDL_SCANCODE_INTERNATIONAL7, "international_7"),
        (_eplatform.SDL_SCANCODE_INTERNATIONAL8, "international_8"),
        (_eplatform.SDL_SCANCODE_INTERNATIONAL9, "international_9"),
        # numpad numbers
        (_eplatform.SDL_SCANCODE_KP_0, "numpad_0"),
        (_eplatform.SDL_SCANCODE_KP_00, "numpad_00"),
        (_eplatform.SDL_SCANCODE_KP_000, "numpad_000"),
        (_eplatform.SDL_SCANCODE_KP_1, "numpad_1"),
        (_eplatform.SDL_SCANCODE_KP_2, "numpad_2"),
        (_eplatform.SDL_SCANCODE_KP_3, "numpad_3"),
        (_eplatform.SDL_SCANCODE_KP_4, "numpad_4"),
        (_eplatform.SDL_SCANCODE_KP_5, "numpad_5"),
        (_eplatform.SDL_SCANCODE_KP_6, "numpad_6"),
        (_eplatform.SDL_SCANCODE_KP_7, "numpad_7"),
        (_eplatform.SDL_SCANCODE_KP_8, "numpad_8"),
        (_eplatform.SDL_SCANCODE_KP_9, "numpad_9"),
        # numpad letters
        (_eplatform.SDL_SCANCODE_KP_A, "numpad_a"),
        (_eplatform.SDL_SCANCODE_KP_B, "numpad_b"),
        (_eplatform.SDL_SCANCODE_KP_C, "numpad_c"),
        (_eplatform.SDL_SCANCODE_KP_D, "numpad_d"),
        (_eplatform.SDL_SCANCODE_KP_E, "numpad_e"),
        (_eplatform.SDL_SCANCODE_KP_F, "numpad_f"),
        # numpad symbols/operators
        (_eplatform.SDL_SCANCODE_KP_AMPERSAND, "numpad_ampersand"),
        (_eplatform.SDL_SCANCODE_KP_AT, "numpad_at"),
        (_eplatform.SDL_SCANCODE_KP_COLON, "numpad_colon"),
        (_eplatform.SDL_SCANCODE_KP_COMMA, "numpad_comma"),
        (_eplatform.SDL_SCANCODE_KP_DBLAMPERSAND, "numpad_and"),
        (_eplatform.SDL_SCANCODE_KP_DBLVERTICALBAR, "numpad_or"),
        (_eplatform.SDL_SCANCODE_KP_DECIMAL, "numpad_decimal"),
        (_eplatform.SDL_SCANCODE_KP_DIVIDE, "numpad_divide"),
        (_eplatform.SDL_SCANCODE_KP_ENTER, "numpad_enter"),
        (_eplatform.SDL_SCANCODE_KP_EQUALS, "numpad_equals"),
        (_eplatform.SDL_SCANCODE_KP_EQUALSAS400, "numpad_as400_equals"),
        (_eplatform.SDL_SCANCODE_KP_EXCLAM, "numpad_bang"),
        (_eplatform.SDL_SCANCODE_KP_GREATER, "numpad_greater"),
        (_eplatform.SDL_SCANCODE_KP_HASH, "numpad_hash"),
        (_eplatform.SDL_SCANCODE_KP_LEFTBRACE, "numpad_left_brace"),
        (_eplatform.SDL_SCANCODE_KP_LEFTPAREN, "numpad_left_parenthesis"),
        (_eplatform.SDL_SCANCODE_KP_LESS, "numpad_less"),
        (_eplatform.SDL_SCANCODE_KP_MINUS, "numpad_minus"),
        (_eplatform.SDL_SCANCODE_KP_MULTIPLY, "numpad_multiply"),
        (_eplatform.SDL_SCANCODE_KP_PERCENT, "numpad_percent"),
        (_eplatform.SDL_SCANCODE_KP_PERIOD, "numpad_period"),
        (_eplatform.SDL_SCANCODE_KP_PLUS, "numpad_plus"),
        (_eplatform.SDL_SCANCODE_KP_PLUSMINUS, "numpad_plus_minus"),
        (_eplatform.SDL_SCANCODE_KP_POWER, "numpad_power"),
        (_eplatform.SDL_SCANCODE_KP_RIGHTBRACE, "numpad_right_brace"),
        (_eplatform.SDL_SCANCODE_KP_RIGHTPAREN, "numpad_right_parenthesis"),
        (_eplatform.SDL_SCANCODE_KP_SPACE, "numpad_space"),
        (_eplatform.SDL_SCANCODE_KP_TAB, "numpad_tab"),
        (_eplatform.SDL_SCANCODE_KP_VERTICALBAR, "numpad_pipe"),
        (_eplatform.SDL_SCANCODE_KP_XOR, "numpad_xor"),
        # numpad actions
        (_eplatform.SDL_SCANCODE_KP_BACKSPACE, "numpad_backspace"),
        (_eplatform.SDL_SCANCODE_KP_BINARY, "numpad_binary"),
        (_eplatform.SDL_SCANCODE_KP_CLEAR, "numpad_clear"),
        (_eplatform.SDL_SCANCODE_KP_CLEARENTRY, "numpad_clear_entry"),
        (_eplatform.SDL_SCANCODE_KP_HEXADECIMAL, "numpad_hexadecimal"),
        (_eplatform.SDL_SCANCODE_KP_OCTAL, "numpad_octal"),
        # memory
        (_eplatform.SDL_SCANCODE_KP_MEMADD, "numpad_memory_add"),
        (_eplatform.SDL_SCANCODE_KP_MEMCLEAR, "numpad_memory_clear"),
        (_eplatform.SDL_SCANCODE_KP_MEMDIVIDE, "numpad_memory_divide"),
        (_eplatform.SDL_SCANCODE_KP_MEMMULTIPLY, "numpad_memory_multiply"),
        (_eplatform.SDL_SCANCODE_KP_MEMRECALL, "numpad_memory_recall"),
        (_eplatform.SDL_SCANCODE_KP_MEMSTORE, "numpad_memory_store"),
        (_eplatform.SDL_SCANCODE_KP_MEMSUBTRACT, "numpad_memory_subtract"),
        # language
        (_eplatform.SDL_SCANCODE_LANG1, "language_1"),
        (_eplatform.SDL_SCANCODE_LANG2, "language_2"),
        (_eplatform.SDL_SCANCODE_LANG3, "language_3"),
        (_eplatform.SDL_SCANCODE_LANG4, "language_4"),
        (_eplatform.SDL_SCANCODE_LANG5, "language_5"),
        (_eplatform.SDL_SCANCODE_LANG6, "language_6"),
        (_eplatform.SDL_SCANCODE_LANG7, "language_7"),
        (_eplatform.SDL_SCANCODE_LANG8, "language_8"),
        (_eplatform.SDL_SCANCODE_LANG9, "language_9"),
    ],
)
@pytest.mark.parametrize("is_pressed", (False, True))
@pytest.mark.parametrize("is_repeat", [False, True])
def test_selector_handle_sdl_event_key_changed(
    mock_keyboard, sdl_scancode, key_name, is_pressed, is_repeat
):
    selector = _Selector()
    assert selector._handle_sdl_event_key_changed(sdl_scancode, is_pressed, is_repeat) == (
        not is_repeat
    )
    if is_repeat:
        assert not mock_keyboard.change_key.called
    else:
        mock_keyboard.change_key.assert_called_once_with(key_name, is_pressed)


@pytest.mark.parametrize("is_pressed", (False, True))
def test_selector_handle_sdl_event_key_changed_unexpected(mock_keyboard, is_pressed):
    selector = _Selector()
    assert not selector._handle_sdl_event_key_changed(0, is_pressed, False)
    mock_keyboard.change_key.assert_not_called()


@pytest.mark.parametrize("text", ["", "hello", "私"])
def test_selector_handle_sdl_event_text_input(mock_window, text):
    selector = _Selector()
    assert selector._handle_sdl_event_text_input(text)
    mock_window.input_text.assert_called_once_with(text)


@pytest.mark.parametrize("x", [25, 45])
@pytest.mark.parametrize("y", [10, 100])
def test_selector_handle_sdl_event_window_resized(mock_window, x, y):
    selector = _Selector()
    size = IVector2(x, y)
    assert selector._handle_sdl_event_window_resized(size)
    assert mock_window.size == size


def test_selector_handle_sdl_event_window_shown(mock_window):
    selector = _Selector()
    assert selector._handle_sdl_event_window_shown()
    assert mock_window.is_visible


def test_selector_handle_sdl_event_window_hidden(mock_window):
    selector = _Selector()
    assert selector._handle_sdl_event_window_hidden()
    assert not mock_window.is_visible
