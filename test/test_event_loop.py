import platform
from contextlib import contextmanager
from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from emath import IVector2

from eplatform import EventLoop
from eplatform import _eplatform
from eplatform import get_displays
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
    clear_sdl_events()
    with patch.object(selector, "_handle_sdl_event") as handle_sdl_event:
        assert not selector._poll_sdl_events()
    assert handle_sdl_event.call_count == 0


def test_selector_poll_sdl_events_none(platform):
    selector = _Selector()
    clear_sdl_events()
    with patch.object(selector, "_handle_sdl_event") as handle_sdl_event:
        assert not selector._poll_sdl_events()
    assert handle_sdl_event.call_count == 0


@pytest.mark.parametrize(
    "event_type",
    [
        _eplatform.SDL_EVENT_QUIT,
        _eplatform.SDL_EVENT_WINDOW_HIDDEN,
        _eplatform.SDL_EVENT_WINDOW_SHOWN,
        _eplatform.SDL_EVENT_WINDOW_FOCUS_GAINED,
        _eplatform.SDL_EVENT_WINDOW_FOCUS_LOST,
    ],
)
def test_selector_poll_sdl_events_default(platform, event_type):
    selector = _Selector()
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
    clear_sdl_events()
    push_sdl_event(event_type, scancode, is_pressed, is_repeat)
    with patch.object(selector, "_handle_sdl_event") as handle_sdl_event:
        assert selector._poll_sdl_events()
    handle_sdl_event.assert_called_once_with(event_type, scancode, is_pressed, is_repeat)


@pytest.mark.parametrize("event_type", [_eplatform.SDL_EVENT_TEXT_INPUT])
@pytest.mark.parametrize("text", ["a", "hello world"])
def test_selector_poll_sdl_events_text_input(platform, event_type, text):
    selector = _Selector()
    clear_sdl_events()
    push_sdl_event(event_type, text)
    with patch.object(selector, "_handle_sdl_event") as handle_sdl_event:
        assert selector._poll_sdl_events()
    handle_sdl_event.assert_called_once_with(event_type, text)


@pytest.mark.parametrize("event_type", [_eplatform.SDL_EVENT_WINDOW_RESIZED])
@pytest.mark.parametrize("size", [IVector2(2, 1), IVector2(99, 75)])
def test_selector_poll_sdl_events_window_resized(platform, event_type, size):
    selector = _Selector()
    clear_sdl_events()
    push_sdl_event(event_type, size.x, size.y)
    with patch.object(selector, "_handle_sdl_event") as handle_sdl_event:
        assert selector._poll_sdl_events()
    handle_sdl_event.assert_called_once_with(event_type, size)


@pytest.mark.parametrize("event_type", [_eplatform.SDL_EVENT_WINDOW_MOVED])
@pytest.mark.parametrize("position", [IVector2(2, 1), IVector2(99, 75)])
def test_selector_poll_sdl_events_window_moved(platform, event_type, position):
    selector = _Selector()
    clear_sdl_events()
    push_sdl_event(event_type, position.x, position.y)
    with patch.object(selector, "_handle_sdl_event") as handle_sdl_event:
        assert selector._poll_sdl_events()
    handle_sdl_event.assert_called_once_with(event_type, position)


@pytest.mark.parametrize(
    "event_type", [_eplatform.SDL_EVENT_DISPLAY_ADDED, _eplatform.SDL_EVENT_DISPLAY_REMOVED]
)
@pytest.mark.parametrize("sdl_display", [1, 100])
def test_selector_poll_sdl_events_display_added_removed(platform, event_type, sdl_display):
    selector = _Selector()
    clear_sdl_events()
    push_sdl_event(event_type, sdl_display)
    with patch.object(selector, "_handle_sdl_event") as handle_sdl_event:
        assert selector._poll_sdl_events()
    handle_sdl_event.assert_called_once_with(event_type, sdl_display)


@pytest.mark.parametrize("event_type", [_eplatform.SDL_EVENT_DISPLAY_ORIENTATION])
@pytest.mark.parametrize("sdl_display", [1, 100])
@pytest.mark.parametrize("orientation", [2, 200])
def test_selector_poll_sdl_events_display_orientation(
    platform, event_type, sdl_display, orientation
):
    selector = _Selector()
    clear_sdl_events()
    push_sdl_event(event_type, sdl_display, orientation)
    with patch.object(selector, "_handle_sdl_event") as handle_sdl_event:
        assert selector._poll_sdl_events()
    handle_sdl_event.assert_called_once_with(event_type, sdl_display, orientation)


move_display = None

if platform.system() == "Windows":

    @contextmanager
    def move_display(display, position):
        import pywintypes
        import win32api
        import win32con

        # find the windows display that matches the Display
        i = -1
        while True:
            i += 1
            try:
                win_display = win32api.EnumDisplayDevices(None, i)
            except pywintypes.error:
                raise RuntimeError("unable to find display")
            try:
                win_display_settings = win32api.EnumDisplaySettingsEx(
                    win_display.DeviceName, win32con.ENUM_CURRENT_SETTINGS
                )
            except pywintypes.error:
                # display is not connected
                continue
            if (
                display.bounds.position.x == win_display_settings.Position_x
                and display.bounds.position.y == win_display_settings.Position_y
            ):
                break
        original_x = win_display_settings.Position_x
        original_y = win_display_settings.Position_y
        win_display_settings.Position_x = position.x
        win_display_settings.Position_y = position.y
        win32api.ChangeDisplaySettingsEx(win_display.DeviceName, win_display_settings, 0)
        try:
            yield
        finally:
            win_display_settings.Position_x = original_x
            win_display_settings.Position_y = original_y
            win32api.ChangeDisplaySettingsEx(win_display.DeviceName, win_display_settings, 0)


@pytest.mark.disruptive
def test_selector_poll_sdl_events_display_moved(platform):
    # The SDL event does not contain the position of the display, we get it from the actual
    # state of the system instead. This means we can't just send a mock event, we need to actually
    # change the state of the system to test this event.

    displays = tuple(get_displays())
    if len(displays) < 2:
        pytest.skip("test requires at least 2 displays")
    if move_display is None:
        pytest.skip("unable to move display on this system")

    display_to_move = [d for d in displays if not d.is_primary][0]
    other_displays = [d for d in displays if d is not display_to_move]
    bottom_right_display = sorted(other_displays, key=lambda d: d.bounds.extent)[-1]
    position = bottom_right_display.bounds.extent + IVector2(0, -1)

    selector = _Selector()
    clear_sdl_events()
    with move_display(display_to_move, position):
        with patch.object(selector, "_handle_sdl_event") as handle_sdl_event:
            selector._poll_sdl_events()
        handle_sdl_event.assert_called_once_with(
            _eplatform.SDL_EVENT_DISPLAY_MOVED, display_to_move._sdl_display, position
        )


change_display_mode = None

if platform.system() == "Windows":

    @contextmanager
    def change_display_mode(display, size, refresh_rate):
        import pywintypes
        import win32api
        import win32con

        # find the windows display that matches the Display
        i = -1
        while True:
            i += 1
            try:
                win_display = win32api.EnumDisplayDevices(None, i)
            except pywintypes.error:
                raise RuntimeError("unable to find display")
            try:
                win_display_settings = win32api.EnumDisplaySettingsEx(
                    win_display.DeviceName, win32con.ENUM_CURRENT_SETTINGS
                )
            except pywintypes.error:
                # display is not connected
                continue
            if (
                display.bounds.position.x == win_display_settings.Position_x
                and display.bounds.position.y == win_display_settings.Position_y
            ):
                break
        # find the closest display mode
        i = -1
        while True:
            i += 1
            try:
                new_win_display_settings = win32api.EnumDisplaySettingsEx(
                    win_display.DeviceName, i
                )
            except pywintypes.error:
                raise RuntimeError("unable to find display mode")
            if (
                new_win_display_settings.PelsWidth == size.x
                and new_win_display_settings.PelsHeight == size.y
                and new_win_display_settings.DisplayFrequency == int(refresh_rate)
            ):
                break

        original_w = win_display_settings.PelsWidth
        original_h = win_display_settings.PelsHeight
        original_r = win_display_settings.DisplayFrequency
        original_b = win_display_settings.BitsPerPel
        win_display_settings.PelsWidth = new_win_display_settings.PelsWidth
        win_display_settings.PelsHeight = new_win_display_settings.PelsHeight
        win_display_settings.DisplayFrequency = new_win_display_settings.DisplayFrequency
        win_display_settings.BitsPerPel = new_win_display_settings.BitsPerPel
        win32api.ChangeDisplaySettingsEx(win_display.DeviceName, win_display_settings, 0)
        try:
            yield new_win_display_settings.DisplayFrequency
        finally:
            win_display_settings.PelsWidth = original_w
            win_display_settings.PelsHeight = original_h
            win_display_settings.DisplayFrequency = original_r
            win_display_settings.BitsPerPel = original_b
            win32api.ChangeDisplaySettingsEx(win_display.DeviceName, win_display_settings, 0)


@pytest.mark.disruptive
def test_selector_poll_sdl_events_mode_changed(platform):
    # The SDL event does not contain the mode of the display, we get it from the actual
    # state of the system instead. This means we can't just send a mock event, we need to actually
    # change the state of the system to test this event.

    displays = tuple(get_displays())
    if len(displays) < 1:
        pytest.skip("test requires at least 1 display")
    if change_display_mode is None:
        pytest.skip("unable to move display on this system")

    display = displays[0]
    different_mode = [m for m in display.modes if m.size != display.bounds.size][0]

    selector = _Selector()
    clear_sdl_events()
    with change_display_mode(display, different_mode.size, different_mode.refresh_rate):
        with patch.object(selector, "_handle_sdl_event") as handle_sdl_event:
            while selector._poll_sdl_events():
                pass
        handle_sdl_event.assert_any_call(
            _eplatform.SDL_EVENT_DISPLAY_CURRENT_MODE_CHANGED,
            display._sdl_display,
            different_mode.size,
            different_mode.refresh_rate,
        )


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
        (_eplatform.SDL_EVENT_WINDOW_MOVED, "_handle_sdl_event_window_moved"),
        (_eplatform.SDL_EVENT_WINDOW_FOCUS_GAINED, "_handle_sdl_event_window_focus_gained"),
        (_eplatform.SDL_EVENT_WINDOW_FOCUS_LOST, "_handle_sdl_event_window_focus_lost"),
        (_eplatform.SDL_EVENT_DISPLAY_ADDED, "_handle_sdl_event_display_added"),
        (_eplatform.SDL_EVENT_DISPLAY_REMOVED, "_handle_sdl_event_display_removed"),
        (_eplatform.SDL_EVENT_DISPLAY_ORIENTATION, "_handle_sdl_event_display_orientation"),
        (_eplatform.SDL_EVENT_DISPLAY_MOVED, "_handle_sdl_event_display_moved"),
        (
            _eplatform.SDL_EVENT_DISPLAY_CURRENT_MODE_CHANGED,
            "_handle_sdl_event_current_mode_changed",
        ),
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
    with patch("eplatform._event_loop.close_window") as close_window:
        assert selector._handle_sdl_event_quit()
    close_window.assert_called_once_with(mock_window)


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


@pytest.mark.parametrize("is_pressed", (False, True))
def test_selector_handle_sdl_mouse_button_changed(mock_mouse, is_pressed):
    selector = _Selector()
    sdl_button = MagicMock()
    with patch("eplatform._event_loop.change_mouse_button") as change_mouse_button:
        assert selector._handle_sdl_event_mouse_button_changed(sdl_button, is_pressed)
    change_mouse_button.assert_called_once_with(mock_mouse, sdl_button, is_pressed)


@pytest.mark.parametrize("is_pressed", (False, True))
@pytest.mark.parametrize("is_repeat", [False, True])
def test_selector_handle_sdl_event_key_changed(mock_keyboard, is_pressed, is_repeat):
    selector = _Selector()
    sdl_scancode = MagicMock()
    with patch("eplatform._event_loop.change_key") as change_key:
        result = selector._handle_sdl_event_key_changed(sdl_scancode, is_pressed, is_repeat)
    if is_repeat:
        assert not result
        assert not change_key.called
    else:
        change_key.assert_called_once_with(mock_keyboard, sdl_scancode, is_pressed)
        assert result == change_key.return_value


@pytest.mark.parametrize("text", ["", "hello", "私"])
def test_selector_handle_sdl_event_text_input(mock_window, text):
    selector = _Selector()
    with patch("eplatform._event_loop.input_window_text") as input_window_text:
        assert selector._handle_sdl_event_text_input(text)
    input_window_text.assert_called_once_with(mock_window, text)


@pytest.mark.parametrize("x", [25, 45])
@pytest.mark.parametrize("y", [10, 100])
def test_selector_handle_sdl_event_window_resized(mock_window, x, y):
    selector = _Selector()
    size = IVector2(x, y)
    with patch("eplatform._event_loop.resize_window") as resize_window:
        assert selector._handle_sdl_event_window_resized(size)
    resize_window.assert_called_once_with(mock_window, size)


@pytest.mark.parametrize("w", [25, 45])
@pytest.mark.parametrize("h", [10, 100])
def test_selector_handle_sdl_event_window_moved(mock_window, w, h):
    selector = _Selector()
    position = IVector2(w, h)
    with patch("eplatform._event_loop.move_window") as move_window:
        assert selector._handle_sdl_event_window_moved(position)
    move_window.assert_called_once_with(mock_window, position)


def test_selector_handle_sdl_event_window_shown(mock_window):
    selector = _Selector()
    with patch("eplatform._event_loop.show_window") as show_window:
        assert selector._handle_sdl_event_window_shown()
    show_window.assert_called_once_with(mock_window)


def test_selector_handle_sdl_event_window_hidden(mock_window):
    selector = _Selector()
    with patch("eplatform._event_loop.hide_window") as hide_window:
        assert selector._handle_sdl_event_window_hidden()
    hide_window.assert_called_once_with(mock_window)


def test_selector_handle_sdl_event_window_focus_gained(mock_window):
    selector = _Selector()
    with patch("eplatform._event_loop.focus_window") as focus_window:
        assert selector._handle_sdl_event_window_focus_gained()
    focus_window.assert_called_once_with(mock_window)


def test_selector_handle_sdl_event_window_focus_lost(mock_window):
    selector = _Selector()
    with patch("eplatform._event_loop.blur_window") as blur_window:
        assert selector._handle_sdl_event_window_focus_lost()
    blur_window.assert_called_once_with(mock_window)


def test_selector_handle_sdl_event_display_added():
    sdl_display = MagicMock()
    selector = _Selector()
    with patch("eplatform._event_loop.connect_display") as connect_display:
        assert selector._handle_sdl_event_display_added(sdl_display)
    connect_display.assert_called_once_with(sdl_display)


def test_selector_handle_sdl_event_display_removed():
    sdl_display = MagicMock()
    selector = _Selector()
    with patch("eplatform._event_loop.disconnect_display") as disconnect_display:
        assert selector._handle_sdl_event_display_removed(sdl_display)
    disconnect_display.assert_called_once_with(sdl_display)


def test_selector_handle_sdl_event_display_orientation():
    sdl_display = MagicMock()
    sdl_display_orientation = MagicMock()
    selector = _Selector()
    with patch("eplatform._event_loop.change_display_orientation") as change_display_orientation:
        assert selector._handle_sdl_event_display_orientation(sdl_display, sdl_display_orientation)
    change_display_orientation.assert_called_once_with(sdl_display, sdl_display_orientation)


def test_selector_handle_sdl_event_display_moved():
    sdl_display = MagicMock()
    position = MagicMock()
    selector = _Selector()
    with patch("eplatform._event_loop.change_display_position") as change_display_position:
        assert selector._handle_sdl_event_display_moved(sdl_display, position)
    change_display_position.assert_called_once_with(sdl_display, position)


def test_handle_sdl_event_current_mode_changed():
    sdl_display = MagicMock()
    size = MagicMock()
    refresh_rate = MagicMock()
    selector = _Selector()
    with (
        patch("eplatform._event_loop.change_display_size") as change_display_size,
        patch("eplatform._event_loop.change_display_refresh_rate") as change_display_refresh_rate,
    ):
        assert selector._handle_sdl_event_current_mode_changed(sdl_display, size, refresh_rate)
    change_display_size.assert_called_once_with(sdl_display, size)
    change_display_refresh_rate.assert_called_once_with(sdl_display, refresh_rate)
