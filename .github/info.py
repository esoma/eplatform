# eplatform
from eplatform import Platform
from eplatform import get_color_bits
from eplatform import get_gl_version

with Platform():
    print("GL Version:", get_gl_version())
    print("Color Bits:", get_color_bits())
