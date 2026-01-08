import os

if hasattr(os, "add_dll_directory"):
    os.add_dll_directory(os.getcwd() + "/vendor/SDL")

from eplatform import OpenGlWindow
from eplatform import Platform
from eplatform import VulkanWindow
from eplatform import get_window

with Platform(window_cls=OpenGlWindow):
    window = get_window()
    print("OpenGL Version:", window.gl_version)
    print("OpenGL Color Bits:", window.gl_color_bits)
    print("OpenGL Depth Bits:", window.gl_depth_bits)
    print("OpenGL Stencil Bits:", window.gl_stencil_bits)

with Platform(window_cls=VulkanWindow):
    window = get_window()
