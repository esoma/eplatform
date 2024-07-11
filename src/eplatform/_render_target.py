from __future__ import annotations

__all__ = ["set_draw_render_target", "RenderTarget"]

# eplatform
from ._platform import Platform

# emath
from emath import IVector2

# pyopengl
from OpenGL.GL import GL_DRAW_FRAMEBUFFER
from OpenGL.GL import glBindFramebuffer
from OpenGL.GL import glViewport

# python
from typing import Protocol


class RenderTarget(Protocol):
    @property
    def gl_framebuffer(self) -> int:
        ...

    @property
    def size(self) -> IVector2:
        ...


_draw_render_target: RenderTarget | None = None


@Platform.register_deactivate_callback
def _reset_state() -> None:
    global _draw_render_target
    _draw_render_target = None


def set_draw_render_target(render_target: RenderTarget) -> None:
    global _draw_render_target
    if _draw_render_target is render_target:
        return
    glBindFramebuffer(GL_DRAW_FRAMEBUFFER, 0)
    glViewport(0, 0, *render_target.size)
    _draw_render_target = render_target
