# eplatform
from eplatform import Platform
from eplatform import get_color_bits
from eplatform import get_depth_bits
from eplatform import get_stencil_bits

with Platform():
    print("Color Bits:", get_color_bits())
    print("Depth Bits:", get_depth_bits())
    print("Stencil Bits:", get_stencil_bits())
