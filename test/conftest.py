# eplatform
from eplatform import Window

# pysdl2
from sdl2 import SDL_INIT_VIDEO
from sdl2 import SDL_InitSubSystem
from sdl2 import SDL_QuitSubSystem

# pytest
import pytest


@pytest.fixture
def _sdl():
    SDL_InitSubSystem(SDL_INIT_VIDEO)
    yield
    SDL_QuitSubSystem(SDL_INIT_VIDEO)


@pytest.fixture
def window(_sdl):
    return Window()
