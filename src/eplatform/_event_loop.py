__all__ = ["EventLoop"]

from asyncio import SelectorEventLoop
from selectors import SelectSelector
from time import time
from typing import Any
from typing import Callable
from typing import Final
from typing import Mapping
from typing import get_args

from emath import IVector2

from . import _eplatform
from ._controller import connect_controller
from ._controller import disconnect_controller
from ._display import change_display_orientation
from ._display import change_display_position
from ._display import change_display_refresh_rate
from ._display import change_display_size
from ._display import connect_display
from ._display import disconnect_display
from ._eplatform import get_sdl_event
from ._keyboard import KeyboardKeyName
from ._mouse import MouseButtonName
from ._platform import get_keyboard
from ._platform import get_mouse
from ._platform import get_window
from ._type import SdlDisplayId
from ._type import SdlDisplayOrientation
from ._type import SdlEventType
from ._type import SdlJoystickId
from ._type import SdlMouseButton
from ._type import SdlScancode
from ._window import blur_window
from ._window import close_window
from ._window import focus_window
from ._window import hide_window
from ._window import input_window_text
from ._window import move_window
from ._window import resize_window
from ._window import show_window


class EventLoop(SelectorEventLoop):
    def __init__(self) -> None:
        super().__init__(_Selector())


class _Selector(SelectSelector):
    def select(self, timeout: float | None = None) -> Any:
        start = time()
        while True:
            events_found = self._poll_sdl_events()
            # don't select block if we've found events
            result = super().select(-1 if events_found else 0.001)
            if result or events_found or (timeout is not None and time() - start > timeout):
                break
        return result

    def _poll_sdl_events(self) -> bool:
        while True:
            event = get_sdl_event()
            if event is None:
                return False
            if self._handle_sdl_event(*event):
                return True

    def _handle_sdl_event(self, event_type: SdlEventType, *args: Any) -> bool:
        try:
            handler = self._SDL_EVENT_DISPATCH[event_type]
        except KeyError:
            return False
        return handler(self, *args)

    def _handle_sdl_event_quit(self) -> bool:
        close_window(get_window())
        return True

    def _handle_sdl_event_mouse_motion(self, position: IVector2, delta: IVector2) -> bool:
        mouse = get_mouse()
        mouse.move(position, delta)
        return True

    def _handle_sdl_event_mouse_wheel(self, delta: IVector2) -> bool:
        mouse = get_mouse()
        mouse.scroll(delta)
        return True

    def _handle_sdl_event_mouse_button_changed(
        self, button: SdlMouseButton, is_pressed: bool
    ) -> bool:
        mouse = get_mouse()
        mouse.change_button(_SDL_MOUSE_BUTTON_TO_NAME[button], is_pressed)
        return True

    def _handle_sdl_event_key_changed(
        self, key: SdlScancode, is_pressed: bool, is_repeat: bool
    ) -> bool:
        if is_repeat:
            return False
        try:
            key_name = _SDL_SCANCODE_TO_NAME[key]
        except KeyError:
            return False
        keyboard = get_keyboard()
        keyboard.change_key(key_name, is_pressed)
        return True

    def _handle_sdl_event_text_input(self, text: str) -> bool:
        input_window_text(get_window(), text)
        return True

    def _handle_sdl_event_window_resized(self, size: IVector2) -> bool:
        resize_window(get_window(), size)
        return True

    def _handle_sdl_event_window_shown(self) -> bool:
        show_window(get_window())
        return True

    def _handle_sdl_event_window_hidden(self) -> bool:
        hide_window(get_window())
        return True

    def _handle_sdl_event_window_moved(self, position: IVector2) -> bool:
        move_window(get_window(), position)
        return True

    def _handle_sdl_event_display_added(self, sdl_display: SdlDisplayId) -> bool:
        connect_display(sdl_display)
        return True

    def _handle_sdl_event_display_removed(self, sdl_display: SdlDisplayId) -> bool:
        disconnect_display(sdl_display)
        return True

    def _handle_sdl_event_display_orientation(
        self, sdl_display: SdlDisplayId, sdl_display_orientation: SdlDisplayOrientation
    ) -> bool:
        change_display_orientation(sdl_display, sdl_display_orientation)
        return True

    def _handle_sdl_event_display_moved(
        self, sdl_display: SdlDisplayId, position: IVector2
    ) -> bool:
        change_display_position(sdl_display, position)
        return True

    def _handle_sdl_event_current_mode_changed(
        self, sdl_display: SdlDisplayId, size: IVector2, refresh_rate: float
    ) -> bool:
        change_display_size(sdl_display, size)
        change_display_refresh_rate(sdl_display, refresh_rate)
        return True

    def _handle_sdl_event_window_focus_gained(self) -> bool:
        focus_window(get_window())
        return True

    def _handle_sdl_event_window_focus_lost(self) -> bool:
        blur_window(get_window())
        return True

    def _handle_sdl_event_joystick_added(self, sdl_joystick: SdlJoystickId) -> bool:
        connect_controller(sdl_joystick)
        return True

    def _handle_sdl_event_joystick_removed(self, sdl_joystick: SdlJoystickId) -> bool:
        disconnect_controller(sdl_joystick)
        return True

    _SDL_EVENT_DISPATCH: Final[Mapping[SdlEventType, Callable[..., bool]]] = {
        _eplatform.SDL_EVENT_QUIT: _handle_sdl_event_quit,
        _eplatform.SDL_EVENT_MOUSE_MOTION: _handle_sdl_event_mouse_motion,
        _eplatform.SDL_EVENT_MOUSE_WHEEL: _handle_sdl_event_mouse_wheel,
        _eplatform.SDL_EVENT_MOUSE_BUTTON_DOWN: _handle_sdl_event_mouse_button_changed,
        _eplatform.SDL_EVENT_MOUSE_BUTTON_UP: _handle_sdl_event_mouse_button_changed,
        _eplatform.SDL_EVENT_KEY_DOWN: _handle_sdl_event_key_changed,
        _eplatform.SDL_EVENT_KEY_UP: _handle_sdl_event_key_changed,
        _eplatform.SDL_EVENT_TEXT_INPUT: _handle_sdl_event_text_input,
        _eplatform.SDL_EVENT_WINDOW_RESIZED: _handle_sdl_event_window_resized,
        _eplatform.SDL_EVENT_WINDOW_SHOWN: _handle_sdl_event_window_shown,
        _eplatform.SDL_EVENT_WINDOW_HIDDEN: _handle_sdl_event_window_hidden,
        _eplatform.SDL_EVENT_WINDOW_MOVED: _handle_sdl_event_window_moved,
        _eplatform.SDL_EVENT_WINDOW_FOCUS_GAINED: _handle_sdl_event_window_focus_gained,
        _eplatform.SDL_EVENT_WINDOW_FOCUS_LOST: _handle_sdl_event_window_focus_lost,
        _eplatform.SDL_EVENT_DISPLAY_ADDED: _handle_sdl_event_display_added,
        _eplatform.SDL_EVENT_DISPLAY_REMOVED: _handle_sdl_event_display_removed,
        _eplatform.SDL_EVENT_DISPLAY_ORIENTATION: _handle_sdl_event_display_orientation,
        _eplatform.SDL_EVENT_DISPLAY_MOVED: _handle_sdl_event_display_moved,
        _eplatform.SDL_EVENT_DISPLAY_CURRENT_MODE_CHANGED: _handle_sdl_event_current_mode_changed,
        _eplatform.SDL_EVENT_JOYSTICK_ADDED: _handle_sdl_event_joystick_added,
        _eplatform.SDL_EVENT_JOYSTICK_REMOVED: _handle_sdl_event_joystick_removed,
    }


_SDL_MOUSE_BUTTON_TO_NAME: Final[Mapping[SdlMouseButton, MouseButtonName]] = {
    _eplatform.SDL_BUTTON_LEFT: "left",
    _eplatform.SDL_BUTTON_MIDDLE: "middle",
    _eplatform.SDL_BUTTON_RIGHT: "right",
    _eplatform.SDL_BUTTON_X1: "back",
    _eplatform.SDL_BUTTON_X2: "forward",
}

_SDL_SCANCODE_TO_NAME: Final[Mapping[SdlScancode, KeyboardKeyName]] = {
    # number
    _eplatform.SDL_SCANCODE_0: "zero",
    _eplatform.SDL_SCANCODE_1: "one",
    _eplatform.SDL_SCANCODE_2: "two",
    _eplatform.SDL_SCANCODE_3: "three",
    _eplatform.SDL_SCANCODE_4: "four",
    _eplatform.SDL_SCANCODE_5: "five",
    _eplatform.SDL_SCANCODE_6: "six",
    _eplatform.SDL_SCANCODE_7: "seven",
    _eplatform.SDL_SCANCODE_8: "eight",
    _eplatform.SDL_SCANCODE_9: "nine",
    # function
    _eplatform.SDL_SCANCODE_F1: "f1",
    _eplatform.SDL_SCANCODE_F2: "f2",
    _eplatform.SDL_SCANCODE_F3: "f3",
    _eplatform.SDL_SCANCODE_F4: "f4",
    _eplatform.SDL_SCANCODE_F5: "f5",
    _eplatform.SDL_SCANCODE_F6: "f6",
    _eplatform.SDL_SCANCODE_F7: "f7",
    _eplatform.SDL_SCANCODE_F8: "f8",
    _eplatform.SDL_SCANCODE_F9: "f9",
    _eplatform.SDL_SCANCODE_F10: "f10",
    _eplatform.SDL_SCANCODE_F11: "f11",
    _eplatform.SDL_SCANCODE_F12: "f12",
    _eplatform.SDL_SCANCODE_F13: "f13",
    _eplatform.SDL_SCANCODE_F14: "f14",
    _eplatform.SDL_SCANCODE_F15: "f15",
    _eplatform.SDL_SCANCODE_F16: "f16",
    _eplatform.SDL_SCANCODE_F17: "f17",
    _eplatform.SDL_SCANCODE_F18: "f18",
    _eplatform.SDL_SCANCODE_F19: "f19",
    _eplatform.SDL_SCANCODE_F20: "f20",
    _eplatform.SDL_SCANCODE_F21: "f21",
    _eplatform.SDL_SCANCODE_F22: "f22",
    _eplatform.SDL_SCANCODE_F23: "f23",
    _eplatform.SDL_SCANCODE_F24: "f24",
    # letters
    _eplatform.SDL_SCANCODE_A: "a",
    _eplatform.SDL_SCANCODE_B: "b",
    _eplatform.SDL_SCANCODE_C: "c",
    _eplatform.SDL_SCANCODE_D: "d",
    _eplatform.SDL_SCANCODE_E: "e",
    _eplatform.SDL_SCANCODE_F: "f",
    _eplatform.SDL_SCANCODE_G: "g",
    _eplatform.SDL_SCANCODE_H: "h",
    _eplatform.SDL_SCANCODE_I: "i",
    _eplatform.SDL_SCANCODE_J: "j",
    _eplatform.SDL_SCANCODE_K: "k",
    _eplatform.SDL_SCANCODE_L: "l",
    _eplatform.SDL_SCANCODE_M: "m",
    _eplatform.SDL_SCANCODE_N: "n",
    _eplatform.SDL_SCANCODE_O: "o",
    _eplatform.SDL_SCANCODE_P: "p",
    _eplatform.SDL_SCANCODE_Q: "q",
    _eplatform.SDL_SCANCODE_R: "r",
    _eplatform.SDL_SCANCODE_S: "s",
    _eplatform.SDL_SCANCODE_T: "t",
    _eplatform.SDL_SCANCODE_U: "u",
    _eplatform.SDL_SCANCODE_V: "v",
    _eplatform.SDL_SCANCODE_W: "w",
    _eplatform.SDL_SCANCODE_X: "x",
    _eplatform.SDL_SCANCODE_Y: "y",
    _eplatform.SDL_SCANCODE_Z: "z",
    # symbols/operators
    _eplatform.SDL_SCANCODE_APOSTROPHE: "apostrophe",
    _eplatform.SDL_SCANCODE_BACKSLASH: "backslash",
    _eplatform.SDL_SCANCODE_COMMA: "comma",
    _eplatform.SDL_SCANCODE_DECIMALSEPARATOR: "decimal_separator",
    _eplatform.SDL_SCANCODE_EQUALS: "equals",
    _eplatform.SDL_SCANCODE_GRAVE: "grave",
    _eplatform.SDL_SCANCODE_LEFTBRACKET: "left_bracket",
    _eplatform.SDL_SCANCODE_MINUS: "minus",
    _eplatform.SDL_SCANCODE_NONUSBACKSLASH: "non_us_backslash",
    _eplatform.SDL_SCANCODE_NONUSHASH: "non_us_hash",
    _eplatform.SDL_SCANCODE_PERIOD: "period",
    _eplatform.SDL_SCANCODE_RIGHTBRACKET: "right_bracket",
    _eplatform.SDL_SCANCODE_RSHIFT: "right_shift",
    _eplatform.SDL_SCANCODE_SEMICOLON: "semicolon",
    _eplatform.SDL_SCANCODE_SEPARATOR: "separator",
    _eplatform.SDL_SCANCODE_SLASH: "slash",
    _eplatform.SDL_SCANCODE_SPACE: "space",
    _eplatform.SDL_SCANCODE_TAB: "tab",
    _eplatform.SDL_SCANCODE_THOUSANDSSEPARATOR: "thousands_separator",
    # actions
    _eplatform.SDL_SCANCODE_AGAIN: "again",
    _eplatform.SDL_SCANCODE_ALTERASE: "alt_erase",
    _eplatform.SDL_SCANCODE_APPLICATION: "context_menu",
    _eplatform.SDL_SCANCODE_BACKSPACE: "backspace",
    _eplatform.SDL_SCANCODE_CANCEL: "cancel",
    _eplatform.SDL_SCANCODE_CAPSLOCK: "capslock",
    _eplatform.SDL_SCANCODE_CLEAR: "clear",
    _eplatform.SDL_SCANCODE_CLEARAGAIN: "clear_again",
    _eplatform.SDL_SCANCODE_COPY: "copy",
    _eplatform.SDL_SCANCODE_CRSEL: "crsel",
    _eplatform.SDL_SCANCODE_CURRENCYSUBUNIT: "currency_sub_unit",
    _eplatform.SDL_SCANCODE_CURRENCYUNIT: "currency_unit",
    _eplatform.SDL_SCANCODE_CUT: "cut",
    _eplatform.SDL_SCANCODE_DELETE: "delete",
    _eplatform.SDL_SCANCODE_END: "end",
    _eplatform.SDL_SCANCODE_ESCAPE: "escape",
    _eplatform.SDL_SCANCODE_EXECUTE: "execute",
    _eplatform.SDL_SCANCODE_EXSEL: "exsel",
    _eplatform.SDL_SCANCODE_FIND: "find",
    _eplatform.SDL_SCANCODE_HELP: "help",
    _eplatform.SDL_SCANCODE_HOME: "home",
    _eplatform.SDL_SCANCODE_INSERT: "insert",
    _eplatform.SDL_SCANCODE_LALT: "left_alt",
    _eplatform.SDL_SCANCODE_LCTRL: "left_control",
    _eplatform.SDL_SCANCODE_LGUI: "left_special",
    _eplatform.SDL_SCANCODE_LSHIFT: "left_shift",
    _eplatform.SDL_SCANCODE_MENU: "menu",
    _eplatform.SDL_SCANCODE_MODE: "mode",
    _eplatform.SDL_SCANCODE_MUTE: "mute",
    _eplatform.SDL_SCANCODE_NUMLOCKCLEAR: "numlock_clear",
    _eplatform.SDL_SCANCODE_OPER: "oper",
    _eplatform.SDL_SCANCODE_OUT: "out",
    _eplatform.SDL_SCANCODE_PAGEDOWN: "page_down",
    _eplatform.SDL_SCANCODE_PAGEUP: "page_up",
    _eplatform.SDL_SCANCODE_PASTE: "paste",
    _eplatform.SDL_SCANCODE_PAUSE: "pause",
    _eplatform.SDL_SCANCODE_POWER: "power",
    _eplatform.SDL_SCANCODE_PRINTSCREEN: "print_screen",
    _eplatform.SDL_SCANCODE_PRIOR: "prior",
    _eplatform.SDL_SCANCODE_RALT: "right_alt",
    _eplatform.SDL_SCANCODE_RCTRL: "right_control",
    _eplatform.SDL_SCANCODE_RETURN: "enter",
    _eplatform.SDL_SCANCODE_RETURN2: "enter_2",
    _eplatform.SDL_SCANCODE_RGUI: "right_special",
    _eplatform.SDL_SCANCODE_SCROLLLOCK: "scroll_lock",
    _eplatform.SDL_SCANCODE_SELECT: "select",
    _eplatform.SDL_SCANCODE_SLEEP: "sleep",
    _eplatform.SDL_SCANCODE_STOP: "stop",
    _eplatform.SDL_SCANCODE_SYSREQ: "system_request",
    _eplatform.SDL_SCANCODE_UNDO: "undo",
    _eplatform.SDL_SCANCODE_VOLUMEDOWN: "volume_down",
    _eplatform.SDL_SCANCODE_VOLUMEUP: "volume_up",
    # media
    _eplatform.SDL_SCANCODE_MEDIA_EJECT: "media_eject",
    _eplatform.SDL_SCANCODE_MEDIA_FAST_FORWARD: "media_fast_forward",
    _eplatform.SDL_SCANCODE_MEDIA_NEXT_TRACK: "media_next_track",
    _eplatform.SDL_SCANCODE_MEDIA_PLAY: "media_play",
    _eplatform.SDL_SCANCODE_MEDIA_PREVIOUS_TRACK: "media_previous_track",
    _eplatform.SDL_SCANCODE_MEDIA_REWIND: "media_rewind",
    _eplatform.SDL_SCANCODE_MEDIA_SELECT: "media_select",
    _eplatform.SDL_SCANCODE_MEDIA_STOP: "media_stop",
    # ac
    _eplatform.SDL_SCANCODE_AC_BACK: "ac_back",
    _eplatform.SDL_SCANCODE_AC_BOOKMARKS: "ac_bookmarks",
    _eplatform.SDL_SCANCODE_AC_FORWARD: "ac_forward",
    _eplatform.SDL_SCANCODE_AC_HOME: "ac_home",
    _eplatform.SDL_SCANCODE_AC_REFRESH: "ac_refresh",
    _eplatform.SDL_SCANCODE_AC_SEARCH: "ac_search",
    _eplatform.SDL_SCANCODE_AC_STOP: "ac_stop",
    # arrows
    _eplatform.SDL_SCANCODE_DOWN: "down",
    _eplatform.SDL_SCANCODE_LEFT: "left",
    _eplatform.SDL_SCANCODE_RIGHT: "right",
    _eplatform.SDL_SCANCODE_UP: "up",
    # international
    _eplatform.SDL_SCANCODE_INTERNATIONAL1: "international_1",
    _eplatform.SDL_SCANCODE_INTERNATIONAL2: "international_2",
    _eplatform.SDL_SCANCODE_INTERNATIONAL3: "international_3",
    _eplatform.SDL_SCANCODE_INTERNATIONAL4: "international_4",
    _eplatform.SDL_SCANCODE_INTERNATIONAL5: "international_5",
    _eplatform.SDL_SCANCODE_INTERNATIONAL6: "international_6",
    _eplatform.SDL_SCANCODE_INTERNATIONAL7: "international_7",
    _eplatform.SDL_SCANCODE_INTERNATIONAL8: "international_8",
    _eplatform.SDL_SCANCODE_INTERNATIONAL9: "international_9",
    # numpad numbers
    _eplatform.SDL_SCANCODE_KP_0: "numpad_0",
    _eplatform.SDL_SCANCODE_KP_00: "numpad_00",
    _eplatform.SDL_SCANCODE_KP_000: "numpad_000",
    _eplatform.SDL_SCANCODE_KP_1: "numpad_1",
    _eplatform.SDL_SCANCODE_KP_2: "numpad_2",
    _eplatform.SDL_SCANCODE_KP_3: "numpad_3",
    _eplatform.SDL_SCANCODE_KP_4: "numpad_4",
    _eplatform.SDL_SCANCODE_KP_5: "numpad_5",
    _eplatform.SDL_SCANCODE_KP_6: "numpad_6",
    _eplatform.SDL_SCANCODE_KP_7: "numpad_7",
    _eplatform.SDL_SCANCODE_KP_8: "numpad_8",
    _eplatform.SDL_SCANCODE_KP_9: "numpad_9",
    # numpad letters
    _eplatform.SDL_SCANCODE_KP_A: "numpad_a",
    _eplatform.SDL_SCANCODE_KP_B: "numpad_b",
    _eplatform.SDL_SCANCODE_KP_C: "numpad_c",
    _eplatform.SDL_SCANCODE_KP_D: "numpad_d",
    _eplatform.SDL_SCANCODE_KP_E: "numpad_e",
    _eplatform.SDL_SCANCODE_KP_F: "numpad_f",
    # numpad symbols/operators
    _eplatform.SDL_SCANCODE_KP_AMPERSAND: "numpad_ampersand",
    _eplatform.SDL_SCANCODE_KP_AT: "numpad_at",
    _eplatform.SDL_SCANCODE_KP_COLON: "numpad_colon",
    _eplatform.SDL_SCANCODE_KP_COMMA: "numpad_comma",
    _eplatform.SDL_SCANCODE_KP_DBLAMPERSAND: "numpad_and",
    _eplatform.SDL_SCANCODE_KP_DBLVERTICALBAR: "numpad_or",
    _eplatform.SDL_SCANCODE_KP_DECIMAL: "numpad_decimal",
    _eplatform.SDL_SCANCODE_KP_DIVIDE: "numpad_divide",
    _eplatform.SDL_SCANCODE_KP_ENTER: "numpad_enter",
    _eplatform.SDL_SCANCODE_KP_EQUALS: "numpad_equals",
    _eplatform.SDL_SCANCODE_KP_EQUALSAS400: "numpad_as400_equals",
    _eplatform.SDL_SCANCODE_KP_EXCLAM: "numpad_bang",
    _eplatform.SDL_SCANCODE_KP_GREATER: "numpad_greater",
    _eplatform.SDL_SCANCODE_KP_HASH: "numpad_hash",
    _eplatform.SDL_SCANCODE_KP_LEFTBRACE: "numpad_left_brace",
    _eplatform.SDL_SCANCODE_KP_LEFTPAREN: "numpad_left_parenthesis",
    _eplatform.SDL_SCANCODE_KP_LESS: "numpad_less",
    _eplatform.SDL_SCANCODE_KP_MINUS: "numpad_minus",
    _eplatform.SDL_SCANCODE_KP_MULTIPLY: "numpad_multiply",
    _eplatform.SDL_SCANCODE_KP_PERCENT: "numpad_percent",
    _eplatform.SDL_SCANCODE_KP_PERIOD: "numpad_period",
    _eplatform.SDL_SCANCODE_KP_PLUS: "numpad_plus",
    _eplatform.SDL_SCANCODE_KP_PLUSMINUS: "numpad_plus_minus",
    _eplatform.SDL_SCANCODE_KP_POWER: "numpad_power",
    _eplatform.SDL_SCANCODE_KP_RIGHTBRACE: "numpad_right_brace",
    _eplatform.SDL_SCANCODE_KP_RIGHTPAREN: "numpad_right_parenthesis",
    _eplatform.SDL_SCANCODE_KP_SPACE: "numpad_space",
    _eplatform.SDL_SCANCODE_KP_TAB: "numpad_tab",
    _eplatform.SDL_SCANCODE_KP_VERTICALBAR: "numpad_pipe",
    _eplatform.SDL_SCANCODE_KP_XOR: "numpad_xor",
    # numpad actions
    _eplatform.SDL_SCANCODE_KP_BACKSPACE: "numpad_backspace",
    _eplatform.SDL_SCANCODE_KP_BINARY: "numpad_binary",
    _eplatform.SDL_SCANCODE_KP_CLEAR: "numpad_clear",
    _eplatform.SDL_SCANCODE_KP_CLEARENTRY: "numpad_clear_entry",
    _eplatform.SDL_SCANCODE_KP_HEXADECIMAL: "numpad_hexadecimal",
    _eplatform.SDL_SCANCODE_KP_OCTAL: "numpad_octal",
    # memory
    _eplatform.SDL_SCANCODE_KP_MEMADD: "numpad_memory_add",
    _eplatform.SDL_SCANCODE_KP_MEMCLEAR: "numpad_memory_clear",
    _eplatform.SDL_SCANCODE_KP_MEMDIVIDE: "numpad_memory_divide",
    _eplatform.SDL_SCANCODE_KP_MEMMULTIPLY: "numpad_memory_multiply",
    _eplatform.SDL_SCANCODE_KP_MEMRECALL: "numpad_memory_recall",
    _eplatform.SDL_SCANCODE_KP_MEMSTORE: "numpad_memory_store",
    _eplatform.SDL_SCANCODE_KP_MEMSUBTRACT: "numpad_memory_subtract",
    # language
    _eplatform.SDL_SCANCODE_LANG1: "language_1",
    _eplatform.SDL_SCANCODE_LANG2: "language_2",
    _eplatform.SDL_SCANCODE_LANG3: "language_3",
    _eplatform.SDL_SCANCODE_LANG4: "language_4",
    _eplatform.SDL_SCANCODE_LANG5: "language_5",
    _eplatform.SDL_SCANCODE_LANG6: "language_6",
    _eplatform.SDL_SCANCODE_LANG7: "language_7",
    _eplatform.SDL_SCANCODE_LANG8: "language_8",
    _eplatform.SDL_SCANCODE_LANG9: "language_9",
}

if __debug__:
    _key_names = set(get_args(KeyboardKeyName))
    _scancode_key_names = set(_SDL_SCANCODE_TO_NAME.values())
    _extra_key_names = _key_names - _scancode_key_names
    assert not _extra_key_names, _extra_key_names
    _extra_scancode_key_names = _scancode_key_names - _key_names
    assert not _extra_scancode_key_names, _extra_scancode_key_names
