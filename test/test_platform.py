# eplatform
from eplatform import Platform
from eplatform import Window
from eplatform import get_gl_version
from eplatform import get_window

# pytest
import pytest


def test_core_already_active(platform):
    platform = Platform()
    with pytest.raises(RuntimeError) as excinfo:
        platform.__enter__()
    assert str(excinfo.value) == "platform already active"


def test_core_instance_not_active():
    platform = Platform()
    with pytest.raises(RuntimeError) as excinfo:
        platform.__exit__()
    assert str(excinfo.value) == "platform instance is not active"


def test_get_window_no_core():
    with pytest.raises(RuntimeError) as excinfo:
        get_window()
    assert str(excinfo.value) == "platform is not active"


def test_get_window(platform):
    window = get_window()
    assert isinstance(window, Window)


def test_get_gl_version_no_core():
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
