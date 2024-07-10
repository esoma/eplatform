from __future__ import annotations

__all__ = ["Keyboard", "KeyboardKey", "KeyboardKeyChanged", "KeyboardKeyName"]

# eevent
from eevent import Event

# python
from typing import Literal
from typing import TypeAlias
from typing import TypedDict
from typing import get_args

KeyboardKeyName: TypeAlias = Literal[
    "zero",
    "one",
    "two",
    "three",
    "four",
    "five",
    "six",
    "seven",
    "eight",
    "nine",
    "f1",
    "f2",
    "f3",
    "f4",
    "f5",
    "f6",
    "f7",
    "f8",
    "f9",
    "f10",
    "f11",
    "f12",
    "f13",
    "f14",
    "f15",
    "f16",
    "f17",
    "f18",
    "f19",
    "f20",
    "f21",
    "f22",
    "f23",
    "f24",
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "q",
    "r",
    "s",
    "t",
    "u",
    "v",
    "w",
    "x",
    "y",
    "z",
    "apostrophe",
    "backslash",
    "comma",
    "decimal_separator",
    "equals",
    "grave",
    "left_bracket",
    "minus",
    "non_us_backslash",
    "non_us_hash",
    "period",
    "right_bracket",
    "right_shift",
    "semicolon",
    "separator",
    "slash",
    "space",
    "tab",
    "thousands_separator",
    "again",
    "alt_erase",
    "start_application_1",
    "start_application_2",
    "context_menu",
    "backspace",
    "brightness_down",
    "brightness_up",
    "calculator",
    "cancel",
    "capslock",
    "clear",
    "clear_again",
    "computer",
    "copy",
    "crsel",
    "currency_sub_unit",
    "currency_unit",
    "cut",
    "delete",
    "display_switch",
    "eject",
    "end",
    "escape",
    "execute",
    "exsel",
    "find",
    "help",
    "home",
    "insert",
    "keyboard_illumination_down",
    "keyboard_illumination_toggle",
    "keyboard_illumination_up",
    "left_alt",
    "left_control",
    "left_special",
    "left_shift",
    "mail",
    "media_select",
    "menu",
    "mode",
    "mute",
    "numlock_clear",
    "oper",
    "out",
    "page_down",
    "page_up",
    "paste",
    "pause",
    "power",
    "print_screen",
    "prior",
    "right_alt",
    "right_control",
    "enter",
    "enter_2",
    "right_special",
    "scroll_lock",
    "select",
    "sleep",
    "stop",
    "system_request",
    "undo",
    "volume_down",
    "volume_up",
    "www",
    "audio_fast_forward",
    "audio_mute",
    "audio_next",
    "audio_play",
    "audio_previous",
    "audio_rewind",
    "audio_stop",
    "ac_back",
    "ac_bookmarks",
    "ac_forward",
    "ac_home",
    "ac_refresh",
    "ac_search",
    "ac_stop",
    "down",
    "left",
    "right",
    "up",
    "international_1",
    "international_2",
    "international_3",
    "international_4",
    "international_5",
    "international_6",
    "international_7",
    "international_8",
    "international_9",
    "numpad_0",
    "numpad_00",
    "numpad_000",
    "numpad_1",
    "numpad_2",
    "numpad_3",
    "numpad_4",
    "numpad_5",
    "numpad_6",
    "numpad_7",
    "numpad_8",
    "numpad_9",
    "numpad_a",
    "numpad_b",
    "numpad_c",
    "numpad_d",
    "numpad_e",
    "numpad_f",
    "numpad_ampersand",
    "numpad_at",
    "numpad_colon",
    "numpad_comma",
    "numpad_and",
    "numpad_or",
    "numpad_decimal",
    "numpad_divide",
    "numpad_enter",
    "numpad_equals",
    "numpad_as400_equals",
    "numpad_bang",
    "numpad_greater",
    "numpad_hash",
    "numpad_left_brace",
    "numpad_left_parenthesis",
    "numpad_less",
    "numpad_minus",
    "numpad_multiply",
    "numpad_percent",
    "numpad_period",
    "numpad_plus",
    "numpad_plus_minus",
    "numpad_power",
    "numpad_right_brace",
    "numpad_right_parenthesis",
    "numpad_space",
    "numpad_tab",
    "numpad_pipe",
    "numpad_xor",
    "numpad_backspace",
    "numpad_binary",
    "numpad_clear",
    "numpad_clear_entry",
    "numpad_hexadecimal",
    "numpad_octal",
    "numpad_memory_add",
    "numpad_memory_clear",
    "numpad_memory_divide",
    "numpad_memory_multiply",
    "numpad_memory_recall",
    "numpad_memory_store",
    "numpad_memory_subtract",
    "language_1",
    "language_2",
    "language_3",
    "language_4",
    "language_5",
    "language_6",
    "language_7",
    "language_8",
    "language_9",
]


class KeyboardKey:
    def __init__(self, name: KeyboardKeyName):
        self.name = name
        self.is_pressed = False

        self.changed: Event[KeyboardKeyChanged] = Event()
        self.pressed: Event[KeyboardKeyChanged] = Event()
        self.released: Event[KeyboardKeyChanged] = Event()

    def __repr__(self) -> str:
        return f"<KeyboardKey {self.name!r}>"


class Keyboard:
    zero: KeyboardKey
    one: KeyboardKey
    two: KeyboardKey
    three: KeyboardKey
    four: KeyboardKey
    five: KeyboardKey
    six: KeyboardKey
    seven: KeyboardKey
    eight: KeyboardKey
    nine: KeyboardKey
    f1: KeyboardKey
    f2: KeyboardKey
    f3: KeyboardKey
    f4: KeyboardKey
    f5: KeyboardKey
    f6: KeyboardKey
    f7: KeyboardKey
    f8: KeyboardKey
    f9: KeyboardKey
    f10: KeyboardKey
    f11: KeyboardKey
    f12: KeyboardKey
    f13: KeyboardKey
    f14: KeyboardKey
    f15: KeyboardKey
    f16: KeyboardKey
    f17: KeyboardKey
    f18: KeyboardKey
    f19: KeyboardKey
    f20: KeyboardKey
    f21: KeyboardKey
    f22: KeyboardKey
    f23: KeyboardKey
    f24: KeyboardKey
    a: KeyboardKey
    b: KeyboardKey
    c: KeyboardKey
    d: KeyboardKey
    e: KeyboardKey
    f: KeyboardKey
    g: KeyboardKey
    h: KeyboardKey
    i: KeyboardKey
    j: KeyboardKey
    k: KeyboardKey
    l: KeyboardKey
    m: KeyboardKey
    n: KeyboardKey
    o: KeyboardKey
    p: KeyboardKey
    q: KeyboardKey
    r: KeyboardKey
    s: KeyboardKey
    t: KeyboardKey
    u: KeyboardKey
    v: KeyboardKey
    w: KeyboardKey
    x: KeyboardKey
    y: KeyboardKey
    z: KeyboardKey
    apostrophe: KeyboardKey
    backslash: KeyboardKey
    comma: KeyboardKey
    decimal_separator: KeyboardKey
    equals: KeyboardKey
    grave: KeyboardKey
    left_bracket: KeyboardKey
    minus: KeyboardKey
    non_us_backslash: KeyboardKey
    non_us_hash: KeyboardKey
    period: KeyboardKey
    right_bracket: KeyboardKey
    right_shift: KeyboardKey
    semicolon: KeyboardKey
    separator: KeyboardKey
    slash: KeyboardKey
    space: KeyboardKey
    tab: KeyboardKey
    thousands_separator: KeyboardKey
    again: KeyboardKey
    alt_erase: KeyboardKey
    start_application_1: KeyboardKey
    start_application_2: KeyboardKey
    context_menu: KeyboardKey
    backspace: KeyboardKey
    brightness_down: KeyboardKey
    brightness_up: KeyboardKey
    calculator: KeyboardKey
    cancel: KeyboardKey
    capslock: KeyboardKey
    clear: KeyboardKey
    clear_again: KeyboardKey
    computer: KeyboardKey
    copy: KeyboardKey
    crsel: KeyboardKey
    currency_sub_unit: KeyboardKey
    currency_unit: KeyboardKey
    cut: KeyboardKey
    delete: KeyboardKey
    display_switch: KeyboardKey
    eject: KeyboardKey
    end: KeyboardKey
    escape: KeyboardKey
    execute: KeyboardKey
    exsel: KeyboardKey
    find: KeyboardKey
    help: KeyboardKey
    home: KeyboardKey
    insert: KeyboardKey
    keyboard_illumination_down: KeyboardKey
    keyboard_illumination_toggle: KeyboardKey
    keyboard_illumination_up: KeyboardKey
    left_alt: KeyboardKey
    left_control: KeyboardKey
    left_special: KeyboardKey
    left_shift: KeyboardKey
    mail: KeyboardKey
    media_select: KeyboardKey
    menu: KeyboardKey
    mode: KeyboardKey
    mute: KeyboardKey
    numlock_clear: KeyboardKey
    oper: KeyboardKey
    out: KeyboardKey
    page_down: KeyboardKey
    page_up: KeyboardKey
    paste: KeyboardKey
    pause: KeyboardKey
    power: KeyboardKey
    print_screen: KeyboardKey
    prior: KeyboardKey
    right_alt: KeyboardKey
    right_control: KeyboardKey
    enter: KeyboardKey
    enter_2: KeyboardKey
    right_special: KeyboardKey
    scroll_lock: KeyboardKey
    select: KeyboardKey
    sleep: KeyboardKey
    stop: KeyboardKey
    system_request: KeyboardKey
    undo: KeyboardKey
    volume_down: KeyboardKey
    volume_up: KeyboardKey
    www: KeyboardKey
    audio_fast_forward: KeyboardKey
    audio_mute: KeyboardKey
    audio_next: KeyboardKey
    audio_play: KeyboardKey
    audio_previous: KeyboardKey
    audio_rewind: KeyboardKey
    audio_stop: KeyboardKey
    ac_back: KeyboardKey
    ac_bookmarks: KeyboardKey
    ac_forward: KeyboardKey
    ac_home: KeyboardKey
    ac_refresh: KeyboardKey
    ac_search: KeyboardKey
    ac_stop: KeyboardKey
    down: KeyboardKey
    left: KeyboardKey
    right: KeyboardKey
    up: KeyboardKey
    international_1: KeyboardKey
    international_2: KeyboardKey
    international_3: KeyboardKey
    international_4: KeyboardKey
    international_5: KeyboardKey
    international_6: KeyboardKey
    international_7: KeyboardKey
    international_8: KeyboardKey
    international_9: KeyboardKey
    numpad_0: KeyboardKey
    numpad_00: KeyboardKey
    numpad_000: KeyboardKey
    numpad_1: KeyboardKey
    numpad_2: KeyboardKey
    numpad_3: KeyboardKey
    numpad_4: KeyboardKey
    numpad_5: KeyboardKey
    numpad_6: KeyboardKey
    numpad_7: KeyboardKey
    numpad_8: KeyboardKey
    numpad_9: KeyboardKey
    numpad_a: KeyboardKey
    numpad_b: KeyboardKey
    numpad_c: KeyboardKey
    numpad_d: KeyboardKey
    numpad_e: KeyboardKey
    numpad_f: KeyboardKey
    numpad_ampersand: KeyboardKey
    numpad_at: KeyboardKey
    numpad_colon: KeyboardKey
    numpad_comma: KeyboardKey
    numpad_and: KeyboardKey
    numpad_or: KeyboardKey
    numpad_decimal: KeyboardKey
    numpad_divide: KeyboardKey
    numpad_enter: KeyboardKey
    numpad_equals: KeyboardKey
    numpad_as400_equals: KeyboardKey
    numpad_bang: KeyboardKey
    numpad_greater: KeyboardKey
    numpad_hash: KeyboardKey
    numpad_left_brace: KeyboardKey
    numpad_left_parenthesis: KeyboardKey
    numpad_less: KeyboardKey
    numpad_minus: KeyboardKey
    numpad_multiply: KeyboardKey
    numpad_percent: KeyboardKey
    numpad_period: KeyboardKey
    numpad_plus: KeyboardKey
    numpad_plus_minus: KeyboardKey
    numpad_power: KeyboardKey
    numpad_right_brace: KeyboardKey
    numpad_right_parenthesis: KeyboardKey
    numpad_space: KeyboardKey
    numpad_tab: KeyboardKey
    numpad_pipe: KeyboardKey
    numpad_xor: KeyboardKey
    numpad_backspace: KeyboardKey
    numpad_binary: KeyboardKey
    numpad_clear: KeyboardKey
    numpad_clear_entry: KeyboardKey
    numpad_hexadecimal: KeyboardKey
    numpad_octal: KeyboardKey
    numpad_memory_add: KeyboardKey
    numpad_memory_clear: KeyboardKey
    numpad_memory_divide: KeyboardKey
    numpad_memory_multiply: KeyboardKey
    numpad_memory_recall: KeyboardKey
    numpad_memory_store: KeyboardKey
    numpad_memory_subtract: KeyboardKey
    language_1: KeyboardKey
    language_2: KeyboardKey
    language_3: KeyboardKey
    language_4: KeyboardKey
    language_5: KeyboardKey
    language_6: KeyboardKey
    language_7: KeyboardKey
    language_8: KeyboardKey
    language_9: KeyboardKey

    def __init__(self) -> None:
        for key_name in get_args(KeyboardKeyName):
            setattr(self, key_name, KeyboardKey(key_name))

        self.key_changed: Event[KeyboardKeyChanged] = Event()
        self.key_pressed: Event[KeyboardKeyChanged] = Event()
        self.key_released: Event[KeyboardKeyChanged] = Event()

    def change_key(self, name: KeyboardKeyName, is_pressed: bool) -> None:
        key: KeyboardKey = getattr(self, name)
        key.is_pressed = is_pressed
        data: KeyboardKeyChanged = {"key": key, "is_pressed": is_pressed}
        self.key_changed(data)
        key.changed(data)
        if is_pressed:
            self.key_pressed(data)
            key.pressed(data)
        else:
            self.key_released(data)
            key.released(data)


class KeyboardKeyChanged(TypedDict):
    key: KeyboardKey
    is_pressed: bool
