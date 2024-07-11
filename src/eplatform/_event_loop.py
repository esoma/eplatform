__all__ = ["EventLoop"]

# eplatform
from ._keyboard import KeyboardKeyName
from ._mouse import MouseButtonName
from ._platform import get_keyboard
from ._platform import get_mouse
from ._platform import get_window

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
from sdl2 import SDL_PRESSED
from sdl2 import SDL_PollEvent
from sdl2 import SDL_QUIT

# python
from asyncio import SelectorEventLoop
from ctypes import byref as c_byref
from selectors import SelectSelector
from time import time
from typing import Any
from typing import Final


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
        event = SDL_Event()
        events_found = False
        while SDL_PollEvent(c_byref(event)) != 0:
            if self._handle_sdl_event(event):
                events_found = True

        return events_found

    def _handle_sdl_event(self, event: SDL_Event) -> bool:
        try:
            handler = self._SDL_EVENT_DISPATCH[event.type]
        except KeyError:
            return False
        return handler(self, event)

    def _handle_sdl_quit(self, event: SDL_Event) -> bool:
        assert event.type == SDL_QUIT
        get_window().closed(None)
        return True

    def _handle_sdl_mouse_motion(self, event: SDL_Event) -> bool:
        assert event.type == SDL_MOUSEMOTION
        mouse = get_mouse()
        mouse.move(
            IVector2(event.motion.x, event.motion.y),
            IVector2(event.motion.xrel, event.motion.yrel),
        )
        return True

    def _handle_sdl_mouse_wheel(self, event: SDL_Event) -> bool:
        assert event.type == SDL_MOUSEWHEEL
        mouse = get_mouse()
        c = -1 if event.wheel.direction == SDL_MOUSEWHEEL_FLIPPED else 1
        mouse.scroll(IVector2(event.wheel.x, event.wheel.y) * c)
        return True

    def _handle_sdl_mouse_button_changed(self, event: SDL_Event) -> bool:
        assert event.type in (SDL_MOUSEBUTTONDOWN, SDL_MOUSEBUTTONUP)
        mouse = get_mouse()
        button_name = self._SDL_MOUSE_BUTTON_TO_NAME[event.button.button]
        mouse.change_button(button_name, event.button.state == SDL_PRESSED)
        return True

    def _handle_sdl_key_changed(self, event: SDL_Event) -> bool:
        assert event.type in (SDL_KEYDOWN, SDL_KEYUP)
        if event.key.repeat != 0:
            return False
        keyboard = get_keyboard()
        try:
            key_name = self._SDL_SCANCODE_TO_NAME[event.key.keysym.scancode]
        except KeyError:
            return False
        keyboard.change_key(key_name, event.key.state == SDL_PRESSED)
        return True

    _SDL_MOUSE_BUTTON_TO_NAME: Final[dict[Any, MouseButtonName]] = {
        SDL_BUTTON_LEFT: "left",
        SDL_BUTTON_MIDDLE: "middle",
        SDL_BUTTON_RIGHT: "right",
        SDL_BUTTON_X1: "back",
        SDL_BUTTON_X2: "forward",
    }

    _SDL_SCANCODE_TO_NAME: Final[dict[Any, KeyboardKeyName]] = {
        # number
        sdl2.SDL_SCANCODE_0: "zero",
        sdl2.SDL_SCANCODE_1: "one",
        sdl2.SDL_SCANCODE_2: "two",
        sdl2.SDL_SCANCODE_3: "three",
        sdl2.SDL_SCANCODE_4: "four",
        sdl2.SDL_SCANCODE_5: "five",
        sdl2.SDL_SCANCODE_6: "six",
        sdl2.SDL_SCANCODE_7: "seven",
        sdl2.SDL_SCANCODE_8: "eight",
        sdl2.SDL_SCANCODE_9: "nine",
        # function
        sdl2.SDL_SCANCODE_F1: "f1",
        sdl2.SDL_SCANCODE_F2: "f2",
        sdl2.SDL_SCANCODE_F3: "f3",
        sdl2.SDL_SCANCODE_F4: "f4",
        sdl2.SDL_SCANCODE_F5: "f5",
        sdl2.SDL_SCANCODE_F6: "f6",
        sdl2.SDL_SCANCODE_F7: "f7",
        sdl2.SDL_SCANCODE_F8: "f8",
        sdl2.SDL_SCANCODE_F9: "f9",
        sdl2.SDL_SCANCODE_F10: "f10",
        sdl2.SDL_SCANCODE_F11: "f11",
        sdl2.SDL_SCANCODE_F12: "f12",
        sdl2.SDL_SCANCODE_F13: "f13",
        sdl2.SDL_SCANCODE_F14: "f14",
        sdl2.SDL_SCANCODE_F15: "f15",
        sdl2.SDL_SCANCODE_F16: "f16",
        sdl2.SDL_SCANCODE_F17: "f17",
        sdl2.SDL_SCANCODE_F18: "f18",
        sdl2.SDL_SCANCODE_F19: "f19",
        sdl2.SDL_SCANCODE_F20: "f20",
        sdl2.SDL_SCANCODE_F21: "f21",
        sdl2.SDL_SCANCODE_F22: "f22",
        sdl2.SDL_SCANCODE_F23: "f23",
        sdl2.SDL_SCANCODE_F24: "f24",
        # letters
        sdl2.SDL_SCANCODE_A: "a",
        sdl2.SDL_SCANCODE_B: "b",
        sdl2.SDL_SCANCODE_C: "c",
        sdl2.SDL_SCANCODE_D: "d",
        sdl2.SDL_SCANCODE_E: "e",
        sdl2.SDL_SCANCODE_F: "f",
        sdl2.SDL_SCANCODE_G: "g",
        sdl2.SDL_SCANCODE_H: "h",
        sdl2.SDL_SCANCODE_I: "i",
        sdl2.SDL_SCANCODE_J: "j",
        sdl2.SDL_SCANCODE_K: "k",
        sdl2.SDL_SCANCODE_L: "l",
        sdl2.SDL_SCANCODE_M: "m",
        sdl2.SDL_SCANCODE_N: "n",
        sdl2.SDL_SCANCODE_O: "o",
        sdl2.SDL_SCANCODE_P: "p",
        sdl2.SDL_SCANCODE_Q: "q",
        sdl2.SDL_SCANCODE_R: "r",
        sdl2.SDL_SCANCODE_S: "s",
        sdl2.SDL_SCANCODE_T: "t",
        sdl2.SDL_SCANCODE_U: "u",
        sdl2.SDL_SCANCODE_V: "v",
        sdl2.SDL_SCANCODE_W: "w",
        sdl2.SDL_SCANCODE_X: "x",
        sdl2.SDL_SCANCODE_Y: "y",
        sdl2.SDL_SCANCODE_Z: "z",
        # symbols/operators
        sdl2.SDL_SCANCODE_APOSTROPHE: "apostrophe",
        sdl2.SDL_SCANCODE_BACKSLASH: "backslash",
        sdl2.SDL_SCANCODE_COMMA: "comma",
        sdl2.SDL_SCANCODE_DECIMALSEPARATOR: "decimal_separator",
        sdl2.SDL_SCANCODE_EQUALS: "equals",
        sdl2.SDL_SCANCODE_GRAVE: "grave",
        sdl2.SDL_SCANCODE_LEFTBRACKET: "left_bracket",
        sdl2.SDL_SCANCODE_MINUS: "minus",
        sdl2.SDL_SCANCODE_NONUSBACKSLASH: "non_us_backslash",
        sdl2.SDL_SCANCODE_NONUSHASH: "non_us_hash",
        sdl2.SDL_SCANCODE_PERIOD: "period",
        sdl2.SDL_SCANCODE_RIGHTBRACKET: "right_bracket",
        sdl2.SDL_SCANCODE_RSHIFT: "right_shift",
        sdl2.SDL_SCANCODE_SEMICOLON: "semicolon",
        sdl2.SDL_SCANCODE_SEPARATOR: "separator",
        sdl2.SDL_SCANCODE_SLASH: "slash",
        sdl2.SDL_SCANCODE_SPACE: "space",
        sdl2.SDL_SCANCODE_TAB: "tab",
        sdl2.SDL_SCANCODE_THOUSANDSSEPARATOR: "thousands_separator",
        # actions
        sdl2.SDL_SCANCODE_AGAIN: "again",
        sdl2.SDL_SCANCODE_ALTERASE: "alt_erase",
        sdl2.SDL_SCANCODE_APP1: "start_application_1",
        sdl2.SDL_SCANCODE_APP2: "start_application_2",
        sdl2.SDL_SCANCODE_APPLICATION: "context_menu",
        sdl2.SDL_SCANCODE_BACKSPACE: "backspace",
        sdl2.SDL_SCANCODE_BRIGHTNESSDOWN: "brightness_down",
        sdl2.SDL_SCANCODE_BRIGHTNESSUP: "brightness_up",
        sdl2.SDL_SCANCODE_CALCULATOR: "calculator",
        sdl2.SDL_SCANCODE_CANCEL: "cancel",
        sdl2.SDL_SCANCODE_CAPSLOCK: "capslock",
        sdl2.SDL_SCANCODE_CLEAR: "clear",
        sdl2.SDL_SCANCODE_CLEARAGAIN: "clear_again",
        sdl2.SDL_SCANCODE_COMPUTER: "computer",
        sdl2.SDL_SCANCODE_COPY: "copy",
        sdl2.SDL_SCANCODE_CRSEL: "crsel",
        sdl2.SDL_SCANCODE_CURRENCYSUBUNIT: "currency_sub_unit",
        sdl2.SDL_SCANCODE_CURRENCYUNIT: "currency_unit",
        sdl2.SDL_SCANCODE_CUT: "cut",
        sdl2.SDL_SCANCODE_DELETE: "delete",
        sdl2.SDL_SCANCODE_DISPLAYSWITCH: "display_switch",
        sdl2.SDL_SCANCODE_EJECT: "eject",
        sdl2.SDL_SCANCODE_END: "end",
        sdl2.SDL_SCANCODE_ESCAPE: "escape",
        sdl2.SDL_SCANCODE_EXECUTE: "execute",
        sdl2.SDL_SCANCODE_EXSEL: "exsel",
        sdl2.SDL_SCANCODE_FIND: "find",
        sdl2.SDL_SCANCODE_HELP: "help",
        sdl2.SDL_SCANCODE_HOME: "home",
        sdl2.SDL_SCANCODE_INSERT: "insert",
        sdl2.SDL_SCANCODE_KBDILLUMDOWN: "keyboard_illumination_down",
        sdl2.SDL_SCANCODE_KBDILLUMTOGGLE: "keyboard_illumination_toggle",
        sdl2.SDL_SCANCODE_KBDILLUMUP: "keyboard_illumination_up",
        sdl2.SDL_SCANCODE_LALT: "left_alt",
        sdl2.SDL_SCANCODE_LCTRL: "left_control",
        sdl2.SDL_SCANCODE_LGUI: "left_special",
        sdl2.SDL_SCANCODE_LSHIFT: "left_shift",
        sdl2.SDL_SCANCODE_MAIL: "mail",
        sdl2.SDL_SCANCODE_MEDIASELECT: "media_select",
        sdl2.SDL_SCANCODE_MENU: "menu",
        sdl2.SDL_SCANCODE_MODE: "mode",
        sdl2.SDL_SCANCODE_MUTE: "mute",
        sdl2.SDL_SCANCODE_NUMLOCKCLEAR: "numlock_clear",
        sdl2.SDL_SCANCODE_OPER: "oper",
        sdl2.SDL_SCANCODE_OUT: "out",
        sdl2.SDL_SCANCODE_PAGEDOWN: "page_down",
        sdl2.SDL_SCANCODE_PAGEUP: "page_up",
        sdl2.SDL_SCANCODE_PASTE: "paste",
        sdl2.SDL_SCANCODE_PAUSE: "pause",
        sdl2.SDL_SCANCODE_POWER: "power",
        sdl2.SDL_SCANCODE_PRINTSCREEN: "print_screen",
        sdl2.SDL_SCANCODE_PRIOR: "prior",
        sdl2.SDL_SCANCODE_RALT: "right_alt",
        sdl2.SDL_SCANCODE_RCTRL: "right_control",
        sdl2.SDL_SCANCODE_RETURN: "enter",
        sdl2.SDL_SCANCODE_RETURN2: "enter_2",
        sdl2.SDL_SCANCODE_RGUI: "right_special",
        sdl2.SDL_SCANCODE_SCROLLLOCK: "scroll_lock",
        sdl2.SDL_SCANCODE_SELECT: "select",
        sdl2.SDL_SCANCODE_SLEEP: "sleep",
        sdl2.SDL_SCANCODE_STOP: "stop",
        sdl2.SDL_SCANCODE_SYSREQ: "system_request",
        sdl2.SDL_SCANCODE_UNDO: "undo",
        sdl2.SDL_SCANCODE_VOLUMEDOWN: "volume_down",
        sdl2.SDL_SCANCODE_VOLUMEUP: "volume_up",
        sdl2.SDL_SCANCODE_WWW: "www",
        # audio
        sdl2.SDL_SCANCODE_AUDIOFASTFORWARD: "audio_fast_forward",
        sdl2.SDL_SCANCODE_AUDIOMUTE: "audio_mute",
        sdl2.SDL_SCANCODE_AUDIONEXT: "audio_next",
        sdl2.SDL_SCANCODE_AUDIOPLAY: "audio_play",
        sdl2.SDL_SCANCODE_AUDIOPREV: "audio_previous",
        sdl2.SDL_SCANCODE_AUDIOREWIND: "audio_rewind",
        sdl2.SDL_SCANCODE_AUDIOSTOP: "audio_stop",
        # ac
        sdl2.SDL_SCANCODE_AC_BACK: "ac_back",
        sdl2.SDL_SCANCODE_AC_BOOKMARKS: "ac_bookmarks",
        sdl2.SDL_SCANCODE_AC_FORWARD: "ac_forward",
        sdl2.SDL_SCANCODE_AC_HOME: "ac_home",
        sdl2.SDL_SCANCODE_AC_REFRESH: "ac_refresh",
        sdl2.SDL_SCANCODE_AC_SEARCH: "ac_search",
        sdl2.SDL_SCANCODE_AC_STOP: "ac_stop",
        # arrows
        sdl2.SDL_SCANCODE_DOWN: "down",
        sdl2.SDL_SCANCODE_LEFT: "left",
        sdl2.SDL_SCANCODE_RIGHT: "right",
        sdl2.SDL_SCANCODE_UP: "up",
        # international
        sdl2.SDL_SCANCODE_INTERNATIONAL1: "international_1",
        sdl2.SDL_SCANCODE_INTERNATIONAL2: "international_2",
        sdl2.SDL_SCANCODE_INTERNATIONAL3: "international_3",
        sdl2.SDL_SCANCODE_INTERNATIONAL4: "international_4",
        sdl2.SDL_SCANCODE_INTERNATIONAL5: "international_5",
        sdl2.SDL_SCANCODE_INTERNATIONAL6: "international_6",
        sdl2.SDL_SCANCODE_INTERNATIONAL7: "international_7",
        sdl2.SDL_SCANCODE_INTERNATIONAL8: "international_8",
        sdl2.SDL_SCANCODE_INTERNATIONAL9: "international_9",
        # numpad numbers
        sdl2.SDL_SCANCODE_KP_0: "numpad_0",
        sdl2.SDL_SCANCODE_KP_00: "numpad_00",
        sdl2.SDL_SCANCODE_KP_000: "numpad_000",
        sdl2.SDL_SCANCODE_KP_1: "numpad_1",
        sdl2.SDL_SCANCODE_KP_2: "numpad_2",
        sdl2.SDL_SCANCODE_KP_3: "numpad_3",
        sdl2.SDL_SCANCODE_KP_4: "numpad_4",
        sdl2.SDL_SCANCODE_KP_5: "numpad_5",
        sdl2.SDL_SCANCODE_KP_6: "numpad_6",
        sdl2.SDL_SCANCODE_KP_7: "numpad_7",
        sdl2.SDL_SCANCODE_KP_8: "numpad_8",
        sdl2.SDL_SCANCODE_KP_9: "numpad_9",
        # numpad letters
        sdl2.SDL_SCANCODE_KP_A: "numpad_a",
        sdl2.SDL_SCANCODE_KP_B: "numpad_b",
        sdl2.SDL_SCANCODE_KP_C: "numpad_c",
        sdl2.SDL_SCANCODE_KP_D: "numpad_d",
        sdl2.SDL_SCANCODE_KP_E: "numpad_e",
        sdl2.SDL_SCANCODE_KP_F: "numpad_f",
        # numpad symbols/operators
        sdl2.SDL_SCANCODE_KP_AMPERSAND: "numpad_ampersand",
        sdl2.SDL_SCANCODE_KP_AT: "numpad_at",
        sdl2.SDL_SCANCODE_KP_COLON: "numpad_colon",
        sdl2.SDL_SCANCODE_KP_COMMA: "numpad_comma",
        sdl2.SDL_SCANCODE_KP_DBLAMPERSAND: "numpad_and",
        sdl2.SDL_SCANCODE_KP_DBLVERTICALBAR: "numpad_or",
        sdl2.SDL_SCANCODE_KP_DECIMAL: "numpad_decimal",
        sdl2.SDL_SCANCODE_KP_DIVIDE: "numpad_divide",
        sdl2.SDL_SCANCODE_KP_ENTER: "numpad_enter",
        sdl2.SDL_SCANCODE_KP_EQUALS: "numpad_equals",
        sdl2.SDL_SCANCODE_KP_EQUALSAS400: "numpad_as400_equals",
        sdl2.SDL_SCANCODE_KP_EXCLAM: "numpad_bang",
        sdl2.SDL_SCANCODE_KP_GREATER: "numpad_greater",
        sdl2.SDL_SCANCODE_KP_HASH: "numpad_hash",
        sdl2.SDL_SCANCODE_KP_LEFTBRACE: "numpad_left_brace",
        sdl2.SDL_SCANCODE_KP_LEFTPAREN: "numpad_left_parenthesis",
        sdl2.SDL_SCANCODE_KP_LESS: "numpad_less",
        sdl2.SDL_SCANCODE_KP_MINUS: "numpad_minus",
        sdl2.SDL_SCANCODE_KP_MULTIPLY: "numpad_multiply",
        sdl2.SDL_SCANCODE_KP_PERCENT: "numpad_percent",
        sdl2.SDL_SCANCODE_KP_PERIOD: "numpad_period",
        sdl2.SDL_SCANCODE_KP_PLUS: "numpad_plus",
        sdl2.SDL_SCANCODE_KP_PLUSMINUS: "numpad_plus_minus",
        sdl2.SDL_SCANCODE_KP_POWER: "numpad_power",
        sdl2.SDL_SCANCODE_KP_RIGHTBRACE: "numpad_right_brace",
        sdl2.SDL_SCANCODE_KP_RIGHTPAREN: "numpad_right_parenthesis",
        sdl2.SDL_SCANCODE_KP_SPACE: "numpad_space",
        sdl2.SDL_SCANCODE_KP_TAB: "numpad_tab",
        sdl2.SDL_SCANCODE_KP_VERTICALBAR: "numpad_pipe",
        sdl2.SDL_SCANCODE_KP_XOR: "numpad_xor",
        # numpad actions
        sdl2.SDL_SCANCODE_KP_BACKSPACE: "numpad_backspace",
        sdl2.SDL_SCANCODE_KP_BINARY: "numpad_binary",
        sdl2.SDL_SCANCODE_KP_CLEAR: "numpad_clear",
        sdl2.SDL_SCANCODE_KP_CLEARENTRY: "numpad_clear_entry",
        sdl2.SDL_SCANCODE_KP_HEXADECIMAL: "numpad_hexadecimal",
        sdl2.SDL_SCANCODE_KP_OCTAL: "numpad_octal",
        # memory
        sdl2.SDL_SCANCODE_KP_MEMADD: "numpad_memory_add",
        sdl2.SDL_SCANCODE_KP_MEMCLEAR: "numpad_memory_clear",
        sdl2.SDL_SCANCODE_KP_MEMDIVIDE: "numpad_memory_divide",
        sdl2.SDL_SCANCODE_KP_MEMMULTIPLY: "numpad_memory_multiply",
        sdl2.SDL_SCANCODE_KP_MEMRECALL: "numpad_memory_recall",
        sdl2.SDL_SCANCODE_KP_MEMSTORE: "numpad_memory_store",
        sdl2.SDL_SCANCODE_KP_MEMSUBTRACT: "numpad_memory_subtract",
        # language
        sdl2.SDL_SCANCODE_LANG1: "language_1",
        sdl2.SDL_SCANCODE_LANG2: "language_2",
        sdl2.SDL_SCANCODE_LANG3: "language_3",
        sdl2.SDL_SCANCODE_LANG4: "language_4",
        sdl2.SDL_SCANCODE_LANG5: "language_5",
        sdl2.SDL_SCANCODE_LANG6: "language_6",
        sdl2.SDL_SCANCODE_LANG7: "language_7",
        sdl2.SDL_SCANCODE_LANG8: "language_8",
        sdl2.SDL_SCANCODE_LANG9: "language_9",
    }

    _SDL_EVENT_DISPATCH: Final = {
        SDL_QUIT: _handle_sdl_quit,
        SDL_MOUSEMOTION: _handle_sdl_mouse_motion,
        SDL_MOUSEWHEEL: _handle_sdl_mouse_wheel,
        SDL_MOUSEBUTTONDOWN: _handle_sdl_mouse_button_changed,
        SDL_MOUSEBUTTONUP: _handle_sdl_mouse_button_changed,
        SDL_KEYDOWN: _handle_sdl_key_changed,
        SDL_KEYUP: _handle_sdl_key_changed,
    }
