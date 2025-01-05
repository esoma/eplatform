import os

if hasattr(os, "add_dll_directory"):
    os.add_dll_directory(os.getcwd() + "/vendor/SDL")

import asyncio

import pytest

from eplatform import EventLoop
from eplatform import Platform
from eplatform import get_keyboard
from eplatform import get_mouse
from eplatform import get_window


def pytest_addoption(parser):
    parser.addoption(
        "--disruptive",
        action="store_true",
        dest="disruptive",
        default=False,
        help="enable tests which might be disruptive or fail due to user interaction",
    )


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "disruptive: a test which might be disruptive or fail due to user interaction"
    )


def pytest_collection_modifyitems(config, items):
    for item in items:
        if not config.option.disruptive and "disruptive" in item.keywords:
            item.add_marker(pytest.mark.skip(reason="skipping disruptive tests"))


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


@pytest.fixture
def capture_event():
    def _(f, e):
        event = None

        async def test():
            nonlocal event
            f()
            event = await asyncio.wait_for(e, timeout=1)

        loop = EventLoop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(test())

        return event

    return _
