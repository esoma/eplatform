# eplatform
from eplatform import Platform
from eplatform import get_mouse
from eplatform import get_window

# pytest
import pytest


@pytest.fixture(autouse=True)
def _reset_platform_callbacks():
    Platform._deactivate_callbacks.clear()


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
