import os

if hasattr(os, "add_dll_directory"):
    os.add_dll_directory(os.getcwd() + "/vendor/SDL")

import asyncio

import pytest

from eplatform import EventLoop
from eplatform import OpenGlWindow
from eplatform import Platform
from eplatform import VulkanWindow
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
    config.addinivalue_line("markers", "opengl: a test which requires an OpenGL window")
    config.addinivalue_line("markers", "vulkan: a test which requires a Vulkan window")


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
def platform(request):
    window_cls = None
    if request.node.get_closest_marker("opengl"):
        window_cls = OpenGlWindow
    elif request.node.get_closest_marker("vulkan"):
        window_cls = VulkanWindow

    platform = Platform(window_cls=window_cls)
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
