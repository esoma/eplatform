from types import GeneratorType
from unittest.mock import Mock
from unittest.mock import patch

import pytest

from eplatform import Keyboard
from eplatform import Mouse
from eplatform import OpenGlWindow
from eplatform import Platform
from eplatform import VulkanWindow
from eplatform import Window
from eplatform import get_clipboard
from eplatform import get_displays
from eplatform import get_keyboard
from eplatform import get_mouse
from eplatform import get_window
from eplatform import set_clipboard


def test_platform_already_active(platform):
    platform = Platform()
    with pytest.raises(RuntimeError) as excinfo:
        platform.__enter__()
    assert str(excinfo.value) == "platform already active"


def test_platform_instance_not_active():
    platform = Platform()
    with pytest.raises(RuntimeError) as excinfo:
        platform.__exit__()
    assert str(excinfo.value) == "platform instance is not active"


@pytest.mark.parametrize(
    "open_gl_version_max",
    [(4, 6), (4, 5), (4, 4), (4, 3), (4, 2), (4, 1), (4, 0), (3, 3), (3, 2), (3, 1)],
)
def test_open_gl_version_max(open_gl_version_max):
    platform = Platform(window_cls=OpenGlWindow, open_gl_version_max=open_gl_version_max)
    with platform:
        assert platform._gl_version <= open_gl_version_max


@pytest.mark.parametrize(
    "open_gl_version_min, open_gl_version_max", [((3, 0), (3, 0)), ((4, 7), (4, 7))]
)
def test_unable_to_create_open_gl_context(open_gl_version_min, open_gl_version_max):
    platform = Platform(
        window_cls=OpenGlWindow,
        open_gl_version_min=open_gl_version_min,
        open_gl_version_max=open_gl_version_max,
    )
    with pytest.raises(RuntimeError) as excinfo:
        with platform:
            pass
    assert str(excinfo.value) == "unable to create open gl context"


def test_get_window_no_platform():
    with pytest.raises(RuntimeError) as excinfo:
        get_window()
    assert str(excinfo.value) == "platform is not active"


def test_get_window(platform):
    window = get_window()
    assert isinstance(window, Window)


def test_get_mouse_no_platform():
    with pytest.raises(RuntimeError) as excinfo:
        get_mouse()
    assert str(excinfo.value) == "platform is not active"


def test_get_mouse(platform):
    mouse = get_mouse()
    assert isinstance(mouse, Mouse)


def test_get_keyboard_no_platform():
    with pytest.raises(RuntimeError) as excinfo:
        get_keyboard()
    assert str(excinfo.value) == "platform is not active"


def test_get_keyboard(platform):
    keyboard = get_keyboard()
    assert isinstance(keyboard, Keyboard)


def test_deactivate_callbacks():
    mock_callback = Mock()
    Platform.register_deactivate_callback(mock_callback)

    with Platform():
        mock_callback.assert_not_called()
    mock_callback.assert_called_once_with()


def test_platform_custom_cls():
    class CustomWindow(Window):
        pass

    class CustomMouse(Mouse):
        pass

    class CustomKeyboard(Keyboard):
        pass

    platform = Platform(
        window_cls=CustomWindow, mouse_cls=CustomMouse, keyboard_cls=CustomKeyboard
    )
    with platform:
        assert isinstance(get_window(), CustomWindow)
        assert isinstance(get_mouse(), CustomMouse)
        assert isinstance(get_keyboard(), CustomKeyboard)


@pytest.mark.parametrize("data", ["", "one two three"])
def test_clipboard(platform, data):
    set_clipboard(data)
    assert get_clipboard() == data


def test_clipboard_no_platform():
    with pytest.raises(RuntimeError) as excinfo:
        set_clipboard("")
    assert str(excinfo.value) == "platform is not active"

    with pytest.raises(RuntimeError) as excinfo:
        get_clipboard()
    assert str(excinfo.value) == "platform is not active"


def test_get_displays(platform):
    displays = [object(), object()]
    with patch("eplatform._platform._get_displays", return_value=displays) as get_displays_mock:
        result = get_displays()
        assert isinstance(result, GeneratorType)
        assert list(result) == displays


def test_get_displays_no_platform():
    with pytest.raises(RuntimeError) as excinfo:
        list(get_displays())
    assert str(excinfo.value) == "platform is not active"


def test_get_displays_platform_lost():
    displays = [object(), object()]
    with patch("eplatform._platform._get_displays", return_value=displays) as get_displays_mock:
        with Platform():
            displays = get_displays()
            d = next(displays)
        with pytest.raises(RuntimeError) as excinfo:
            next(displays)
        assert str(excinfo.value) == "platform is not active"


def test_vulkan_window():
    platform = Platform(window_cls=VulkanWindow)
    with platform:
        window = get_window()
        assert isinstance(window, VulkanWindow)
