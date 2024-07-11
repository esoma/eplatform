# eplatform
from eplatform import Platform
from eplatform import set_draw_render_target
import eplatform._render_target
from eplatform._render_target import _reset_state

# pyopengl
from OpenGL.GL import GL_DRAW_FRAMEBUFFER

# python
from unittest.mock import patch


def test_default_state():
    assert eplatform._render_target._draw_render_target is None
    assert _reset_state in Platform._deactivate_callbacks


def test_reset_state():
    eplatform._render_target._draw_render_target = 1
    _reset_state()
    assert eplatform._render_target._draw_render_target is None


@patch("eplatform._render_target.glBindFramebuffer")
@patch("eplatform._render_target.glViewport")
def test_set_draw_window(glViewport, glBindFramebuffer, window):
    set_draw_render_target(window)
    assert eplatform._render_target._draw_render_target is window
    glBindFramebuffer.assert_called_once_with(GL_DRAW_FRAMEBUFFER, 0)
    glViewport.assert_called_once_with(0, 0, *window.size)

    glBindFramebuffer.reset_mock()
    glViewport.reset_mock()
    set_draw_render_target(window)
    assert eplatform._render_target._draw_render_target is window
    glBindFramebuffer.assert_not_called()
    glViewport.assert_not_called()
