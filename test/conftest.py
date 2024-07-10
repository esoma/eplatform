# eplatform
from eplatform import Platform
from eplatform import get_window

# pytest
import pytest


@pytest.fixture
def platform():
    platform = Platform()
    with platform:
        yield platform


@pytest.fixture
def window(platform):
    return get_window()
