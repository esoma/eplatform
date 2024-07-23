# eplatform
from eplatform import Keyboard
from eplatform import Mouse
from eplatform import Platform
from eplatform import Window
from eplatform import get_clipboard
from eplatform import get_color_bits
from eplatform import get_depth_bits
from eplatform import get_keyboard
from eplatform import get_mouse
from eplatform import get_stencil_bits
from eplatform import get_window
from eplatform import set_clipboard

# pytest
import pytest

# python
from unittest.mock import Mock


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


def test_get_color_bits_no_platform():
    with pytest.raises(RuntimeError) as excinfo:
        get_color_bits()
    assert str(excinfo.value) == "platform is not active"


def test_get_color_bits(platform):
    color_bits = get_color_bits()
    assert isinstance(color_bits, tuple)
    assert len(color_bits) == 4
    assert all(isinstance(b, int) for b in color_bits)


def test_get_depth_bits_no_platform():
    with pytest.raises(RuntimeError) as excinfo:
        get_depth_bits()
    assert str(excinfo.value) == "platform is not active"


def test_get_depth_bits(platform):
    depth_bits = get_depth_bits()
    assert isinstance(depth_bits, int)


def test_get_stencil_bits_no_platform():
    with pytest.raises(RuntimeError) as excinfo:
        get_stencil_bits()
    assert str(excinfo.value) == "platform is not active"


def test_get_stencil_bits(platform):
    stencil_bits = get_stencil_bits()
    assert isinstance(stencil_bits, int)


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


@pytest.mark.parametrize("data", [b"", b"one two three"])
def test_clipboard(platform, data):
    set_clipboard(data)
    assert get_clipboard() == data


def test_clipboard_no_platform():
    with pytest.raises(RuntimeError) as excinfo:
        set_clipboard(b"")
    assert str(excinfo.value) == "platform is not active"

    with pytest.raises(RuntimeError) as excinfo:
        get_clipboard()
    assert str(excinfo.value) == "platform is not active"
