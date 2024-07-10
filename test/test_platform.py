# eplatform
from eplatform import Keyboard
from eplatform import Mouse
from eplatform import Platform
from eplatform import Window
from eplatform import get_gl_version
from eplatform import get_keyboard
from eplatform import get_mouse
from eplatform import get_window

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


def test_get_gl_version_no_platform():
    with pytest.raises(RuntimeError) as excinfo:
        get_gl_version()
    assert str(excinfo.value) == "platform is not active"


def test_get_gl_version(platform):
    gl_version = get_gl_version()
    assert gl_version in [
        (4, 6),
        (4, 5),
        (4, 4),
        (4, 3),
        (4, 2),
        (4, 1),
        (4, 0),
        (3, 3),
        (3, 2),
        (3, 1),
    ]


def test_deactivate_callbacks():
    mock_callback = Mock()
    Platform.register_deactivate_callback(mock_callback)

    with Platform():
        mock_callback.assert_not_called()
    mock_callback.assert_called_once_with()
