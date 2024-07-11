# eplatform
from eplatform import Platform
from eplatform import get_keyboard
from eplatform import get_mouse
from eplatform import get_window

# pytest
import pytest


@pytest.fixture(autouse=True)
def _reset_platform_callbacks():
    callbacks = list(Platform._deactivate_callbacks)
    yield
    Platform._deactivate_callbacks = callbacks


@pytest.fixture
def platform():
    platform = Platform()
    with platform:
        yield platform


@pytest.fixture
def window(platform):
    return get_window()


@pytest.fixture
def mouse(platform):
    return get_mouse()


@pytest.fixture
def keyboard(platform):
    return get_keyboard()
