
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <SDL3/SDL.h>

#include "emath.h"

#define CHECK_UNEXPECTED_ARG_COUNT_ERROR(expected_count)\
    if (expected_count != nargs)\
    {\
        PyErr_Format(PyExc_TypeError, "expected %zi args, got %zi", expected_count, nargs);\
        goto error;\
    }

#define CHECK_UNEXPECTED_PYTHON_ERROR()\
    if (PyErr_Occurred())\
    {\
        goto error;\
    }

#define RAISE_SDL_ERROR()\
    {\
        PyObject *cause = PyErr_GetRaisedException();\
        PyErr_Format(\
            PyExc_RuntimeError,\
            "sdl error: %s\nfile: %s\nfunction: %s\nline: %i",\
            SDL_GetError(),\
            __FILE__,\
            __func__,\
            __LINE__\
        );\
        if (cause)\
        {\
            PyObject *ex = PyErr_GetRaisedException();\
            PyErr_SetRaisedException(ex);\
            PyException_SetCause(ex, cause);\
            if (cause){ Py_DECREF(cause); cause = 0; }\
        }\
        goto error;\
    }

static const int SUB_SYSTEMS = SDL_INIT_VIDEO;

typedef struct ModuleState
{
    int dummy;
} ModuleState;

static PyObject *
reset_module_state(PyObject *module, PyObject *unused)
{
    ModuleState *state = (ModuleState *)PyModule_GetState(module);
    CHECK_UNEXPECTED_PYTHON_ERROR();
    if (!state){ Py_RETURN_NONE; }

    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
initialize_sdl(PyObject *module, PyObject *unused)
{
    if (!SDL_InitSubSystem(SUB_SYSTEMS)){ RAISE_SDL_ERROR(); }
    SDL_SetHint("SDL_HINT_IME_SHOW_UI", "1");
    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
deinitialize_sdl(PyObject *module, PyObject *unused)
{
    SDL_QuitSubSystem(SUB_SYSTEMS);
    SDL_Quit();
    Py_RETURN_NONE;
}

static PyObject *
create_sdl_window(PyObject *module, PyObject *unused)
{
    SDL_Window *sdl_window = SDL_CreateWindow("", 200, 200, SDL_WINDOW_HIDDEN | SDL_WINDOW_OPENGL);
    if (!sdl_window){ RAISE_SDL_ERROR(); }
    if (!SDL_StopTextInput(sdl_window)){ RAISE_SDL_ERROR(); }

    PyObject *py_sdl_window = PyCapsule_New(sdl_window, "_eplatform.SDL_Window", 0);
    if (!py_sdl_window){ goto error; }
    return py_sdl_window;
error:
    if (sdl_window){ SDL_DestroyWindow(sdl_window); }
    return 0;
}

static PyObject *
delete_sdl_window(PyObject *module, PyObject *py_sdl_window)
{
    SDL_Window *sdl_window = PyCapsule_GetPointer(py_sdl_window, "_eplatform.SDL_Window");
    if (!sdl_window){ goto error; }
    SDL_DestroyWindow(sdl_window);
    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
show_sdl_window(PyObject *module, PyObject *py_sdl_window)
{
    SDL_Window *sdl_window = PyCapsule_GetPointer(py_sdl_window, "_eplatform.SDL_Window");
    if (!sdl_window){ goto error; }
    if (!SDL_ShowWindow(sdl_window)){ RAISE_SDL_ERROR(); }
    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
hide_sdl_window(PyObject *module, PyObject *py_sdl_window)
{
    SDL_Window *sdl_window = PyCapsule_GetPointer(py_sdl_window, "_eplatform.SDL_Window");
    if (!sdl_window){ goto error; }
    if (!SDL_HideWindow(sdl_window)){ RAISE_SDL_ERROR(); }
    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
set_sdl_window_size(PyObject *module, PyObject **args, Py_ssize_t nargs)
{
    PyObject *ex = 0;
    struct EMathApi *emath_api = 0;

    CHECK_UNEXPECTED_ARG_COUNT_ERROR(2);

    SDL_Window *sdl_window = PyCapsule_GetPointer(args[0], "_eplatform.SDL_Window");
    if (!sdl_window){ goto error; }

    emath_api = EMathApi_Get();
    CHECK_UNEXPECTED_PYTHON_ERROR();

    const int *size = emath_api->IVector2_GetValuePointer(args[1]);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    EMathApi_Release();
    emath_api = 0;

    if (!SDL_SetWindowSize(sdl_window, size[0], size[1])){ RAISE_SDL_ERROR(); }

    Py_RETURN_NONE;
error:
    ex = PyErr_GetRaisedException();
    if (emath_api){ EMathApi_Release(); }
    PyErr_SetRaisedException(ex);
    return 0;
}

static PyObject *
center_sdl_window(PyObject *module, PyObject *py_sdl_window)
{
    SDL_Window *sdl_window = PyCapsule_GetPointer(py_sdl_window, "_eplatform.SDL_Window");
    if (!sdl_window){ goto error; }
    if (!SDL_SetWindowPosition(sdl_window, SDL_WINDOWPOS_CENTERED, SDL_WINDOWPOS_CENTERED))
    {
        RAISE_SDL_ERROR();
    }
    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
swap_sdl_window(PyObject *module, PyObject **args, Py_ssize_t nargs)
{
    CHECK_UNEXPECTED_ARG_COUNT_ERROR(2);

    SDL_Window *sdl_window = PyCapsule_GetPointer(args[0], "_eplatform.SDL_Window");
    if (!sdl_window){ goto error; }

    long sync = PyLong_AsLong(args[1]);
    if (sync == -1){ CHECK_UNEXPECTED_PYTHON_ERROR(); }

    while(true)
    {
        if (SDL_GL_SetSwapInterval(sync)){ break; }
        // not all systems support adaptive vsync, so try regular vsync
        // instead
        if (sync == -1) // adaptive
        {
            sync = 1;
        }
        else
        {
            // not all systems are double buffered, so setting any swap
            // interval will result in an error
            // we don't actually need to swap the window in this case
            Py_RETURN_NONE;
        }
    }

    SDL_GL_SwapWindow(sdl_window);

    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
enable_sdl_window_text_input(PyObject *module, PyObject **args, Py_ssize_t nargs)
{
    CHECK_UNEXPECTED_ARG_COUNT_ERROR(6);

    SDL_Window *sdl_window = PyCapsule_GetPointer(args[0], "_eplatform.SDL_Window");
    if (!sdl_window){ goto error; }

    SDL_Rect rect;
    rect.x = PyLong_AsLong(args[1]);
    if (rect.x == -1){ CHECK_UNEXPECTED_PYTHON_ERROR(); }
    rect.y = PyLong_AsLong(args[2]);
    if (rect.y == -1){ CHECK_UNEXPECTED_PYTHON_ERROR(); }
    rect.w = PyLong_AsLong(args[3]);
    if (rect.w == -1){ CHECK_UNEXPECTED_PYTHON_ERROR(); }
    rect.h = PyLong_AsLong(args[4]);
    if (rect.h == -1){ CHECK_UNEXPECTED_PYTHON_ERROR(); }

    int cursor = PyLong_AsLong(args[5]);
    if (cursor == -1){ CHECK_UNEXPECTED_PYTHON_ERROR(); }

    if (!SDL_SetTextInputArea(sdl_window, &rect, cursor)){ RAISE_SDL_ERROR(); }
    if (!SDL_StartTextInput(sdl_window)){ RAISE_SDL_ERROR(); }

    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
disable_sdl_window_text_input(PyObject *module, PyObject *py_sdl_window)
{
    SDL_Window *sdl_window = PyCapsule_GetPointer(py_sdl_window, "_eplatform.SDL_Window");
    if (!sdl_window){ goto error; }

    if (!SDL_StopTextInput(sdl_window)){ RAISE_SDL_ERROR(); }

    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
create_sdl_gl_context(PyObject *module, PyObject *py_sdl_window)
{
    SDL_GLContext sdl_gl_context = 0;

    SDL_Window *sdl_window = PyCapsule_GetPointer(py_sdl_window, "_eplatform.SDL_Window");
    if (!sdl_window){ goto error; }

    if (!SDL_GL_SetAttribute(SDL_GL_CONTEXT_PROFILE_MASK, SDL_GL_CONTEXT_PROFILE_CORE))
    {
        RAISE_SDL_ERROR();
    }
    static const int gl_versions[][2] = {
        {4, 6},
        {4, 5},
        {4, 4},
        {4, 3},
        {4, 2},
        {4, 1},
        {4, 0},
        {3, 3},
        {3, 2},
        {3, 1},
    };
    for (size_t i = 0; i < (sizeof(gl_versions) / sizeof(int) * 2); i++)
    {
        if (!SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, gl_versions[i][0]))
        {
            RAISE_SDL_ERROR();
        }
        if (!SDL_GL_SetAttribute(SDL_GL_CONTEXT_MAJOR_VERSION, gl_versions[i][1]))
        {
            RAISE_SDL_ERROR();
        }
        sdl_gl_context = SDL_GL_CreateContext(sdl_window);
        if (sdl_gl_context){ break; }
    }
    if (!sdl_gl_context){ RAISE_SDL_ERROR(); }

    PyObject *py_sdl_gl_context = PyCapsule_New(sdl_gl_context, "_eplatform.SDL_GLContext", 0);
    if (!py_sdl_gl_context){ goto error; }
    return py_sdl_gl_context;
error:
    if (sdl_gl_context)
    {
        if (!SDL_GL_DestroyContext(sdl_gl_context))
        {
            RAISE_SDL_ERROR();
        }
    }
    return 0;
}

static PyObject *
delete_sdl_gl_context(PyObject *module, PyObject *py_sdl_gl_context)
{
    SDL_GLContext sdl_gl_context = PyCapsule_GetPointer(
        py_sdl_gl_context,
        "_eplatform.SDL_GLContext"
    );
    if (!sdl_gl_context){ goto error; }
    if (!SDL_GL_DestroyContext(sdl_gl_context)){ RAISE_SDL_ERROR(); }
    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
get_gl_attrs(PyObject *module, PyObject *unused)
{
    int red;
    int green;
    int blue;
    int alpha;
    int depth;
    int stencil;

    if (!SDL_GL_GetAttribute(SDL_GL_RED_SIZE, &red)){ RAISE_SDL_ERROR(); }
    if (!SDL_GL_GetAttribute(SDL_GL_GREEN_SIZE, &green)){ RAISE_SDL_ERROR(); }
    if (!SDL_GL_GetAttribute(SDL_GL_BLUE_SIZE, &blue)){ RAISE_SDL_ERROR(); }
    if (!SDL_GL_GetAttribute(SDL_GL_ALPHA_SIZE, &alpha)){ RAISE_SDL_ERROR(); }
    if (!SDL_GL_GetAttribute(SDL_GL_DEPTH_SIZE, &depth)){ RAISE_SDL_ERROR(); }
    if (!SDL_GL_GetAttribute(SDL_GL_STENCIL_SIZE, &stencil)){ RAISE_SDL_ERROR(); }

    return Py_BuildValue("(iiiiii)", red, green, blue, alpha, depth, stencil);
error:
    return 0;
}

static PyObject *
set_clipboard(PyObject *module, PyObject *py_str)
{
    Py_ssize_t str_size;
    const char *str = PyUnicode_AsUTF8AndSize(py_str, &str_size);
    if (!str){ goto error; }
    /*if (str_size == 0)
    {
        if (!SDL_ClearClipboardData()){ RAISE_SDL_ERROR(); }
    }
    else*/
    {
        if (!SDL_SetClipboardText(str)){ RAISE_SDL_ERROR(); }
    }
    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
get_clipboard(PyObject *module, PyObject *unused)
{
    char *str = SDL_GetClipboardText();
    if (!str)
    {
        SDL_free(str);
        if (SDL_HasClipboardText())
        {
            RAISE_SDL_ERROR();
        }
        return PyUnicode_FromString("");
    }
    PyObject *py_str = PyUnicode_FromString(str);
    SDL_free(str);
    return py_str;
error:
    return 0;
}

static PyObject *
clear_sdl_events(PyObject *module, PyObject *unused)
{
    SDL_PumpEvents();
    SDL_FlushEvents(SDL_EVENT_FIRST, SDL_EVENT_LAST);
    Py_RETURN_NONE;
}

static PyObject *
push_sdl_event(PyObject *module, PyObject **args, Py_ssize_t nargs)
{
    if (nargs == 0)
    {
        PyErr_Format(PyExc_TypeError, "expected at least 1 arg, got %zi",  nargs);
        goto error;
    }

    SDL_Event event;
    event.type = PyLong_AsLong(args[0]);
    CHECK_UNEXPECTED_PYTHON_ERROR();

    switch(event.type)
    {
        case SDL_EVENT_MOUSE_MOTION:
        {
            CHECK_UNEXPECTED_ARG_COUNT_ERROR(5);
            event.motion.x = (float)PyLong_AsLong(args[1]);
            CHECK_UNEXPECTED_PYTHON_ERROR();
            event.motion.y = (float)PyLong_AsLong(args[2]);
            CHECK_UNEXPECTED_PYTHON_ERROR();
            event.motion.xrel = (float)PyLong_AsLong(args[3]);
            CHECK_UNEXPECTED_PYTHON_ERROR();
            event.motion.yrel = (float)PyLong_AsLong(args[4]);
            CHECK_UNEXPECTED_PYTHON_ERROR();
            break;
        }
        case SDL_EVENT_MOUSE_WHEEL:
        {
            CHECK_UNEXPECTED_ARG_COUNT_ERROR(4);

            event.wheel.direction = SDL_MOUSEWHEEL_NORMAL;
            if (args[1] == Py_True)
            {
                event.wheel.direction = SDL_MOUSEWHEEL_FLIPPED;
            }
            event.wheel.x = (float)PyLong_AsLong(args[2]);
            CHECK_UNEXPECTED_PYTHON_ERROR();
            event.wheel.y = (float)PyLong_AsLong(args[3]);
            CHECK_UNEXPECTED_PYTHON_ERROR();
            break;
        }
        case SDL_EVENT_MOUSE_BUTTON_DOWN:
        case SDL_EVENT_MOUSE_BUTTON_UP:
        {
            CHECK_UNEXPECTED_ARG_COUNT_ERROR(3);

            event.button.button = (Uint8)PyLong_AsLong(args[1]);
            CHECK_UNEXPECTED_PYTHON_ERROR();
            event.button.down = args[2] == Py_True;
            break;
        }
        case SDL_EVENT_KEY_DOWN:
        case SDL_EVENT_KEY_UP:
        {
            CHECK_UNEXPECTED_ARG_COUNT_ERROR(4);

            event.key.scancode = PyLong_AsLong(args[1]);
            CHECK_UNEXPECTED_PYTHON_ERROR();
            event.key.down = args[2] == Py_True;
            event.key.repeat = args[3] == Py_True;
            break;
        }
        case SDL_EVENT_TEXT_INPUT:
        {
            CHECK_UNEXPECTED_ARG_COUNT_ERROR(2);
            event.text.text = PyUnicode_AsUTF8(args[1]);
            CHECK_UNEXPECTED_PYTHON_ERROR();
            break;
        }
        case SDL_EVENT_WINDOW_RESIZED:
        {
            CHECK_UNEXPECTED_ARG_COUNT_ERROR(3);

            event.window.data1 = PyLong_AsLong(args[1]);
            CHECK_UNEXPECTED_PYTHON_ERROR();
            event.window.data2 = PyLong_AsLong(args[2]);
            CHECK_UNEXPECTED_PYTHON_ERROR();
            break;
        }
    }

    if (!SDL_PushEvent(&event)){ RAISE_SDL_ERROR(); }

    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
get_sdl_event(PyObject *module, PyObject *unused)
{
    PyObject *ex = 0;
    struct EMathApi *emath_api = 0;

    SDL_Event event;
    int result = SDL_PollEvent(&event);
    if (result == 0)
    {
        Py_RETURN_NONE;
    }

    switch(event.type)
    {
        case SDL_EVENT_MOUSE_MOTION:
        {
            emath_api = EMathApi_Get();
            CHECK_UNEXPECTED_PYTHON_ERROR();

            const int position[2] = {(int)event.motion.x, (int)event.motion.y};
            PyObject *py_position = emath_api->IVector2_Create(position);
            CHECK_UNEXPECTED_PYTHON_ERROR();

            const int delta[2] = {(int)event.motion.xrel, (int)event.motion.yrel};
            PyObject *py_delta = emath_api->IVector2_Create(delta);
            CHECK_UNEXPECTED_PYTHON_ERROR();

            EMathApi_Release();
            emath_api = 0;

            return Py_BuildValue("(iOO)", event.type, py_position, py_delta);
        }
        case SDL_EVENT_MOUSE_WHEEL:
        {
            emath_api = EMathApi_Get();
            CHECK_UNEXPECTED_PYTHON_ERROR();

            int c = 1;
            if (event.wheel.direction == SDL_MOUSEWHEEL_FLIPPED)
            {
                c = -1;
            }

            const int delta[2] = {(int)event.wheel.x * c, (int)event.wheel.y * c};
            PyObject *py_delta = emath_api->IVector2_Create(delta);
            CHECK_UNEXPECTED_PYTHON_ERROR();

            EMathApi_Release();
            emath_api = 0;

            return Py_BuildValue("(iO)", event.type, py_delta);
        }
        case SDL_EVENT_MOUSE_BUTTON_DOWN:
        case SDL_EVENT_MOUSE_BUTTON_UP:
        {
            return Py_BuildValue(
                "(iBO)",
                event.type,
                event.button.button,
                event.button.down ? Py_True : Py_False
            );
        }
        case SDL_EVENT_KEY_DOWN:
        case SDL_EVENT_KEY_UP:
        {
            return Py_BuildValue(
                "(iiOO)",
                event.type,
                event.key.scancode,
                event.key.down ? Py_True : Py_False,
                event.key.repeat ? Py_True: Py_False
            );
        }
        case SDL_EVENT_TEXT_INPUT:
        {
            return Py_BuildValue("(is)", event.type, event.text.text);
        }
        case SDL_EVENT_WINDOW_RESIZED:
        {
            emath_api = EMathApi_Get();
            CHECK_UNEXPECTED_PYTHON_ERROR();

            const int size[2] = {(int)event.window.data1, (int)event.window.data2};
            PyObject *py_size = emath_api->IVector2_Create(size);
            CHECK_UNEXPECTED_PYTHON_ERROR();

            EMathApi_Release();
            emath_api = 0;

            return Py_BuildValue("(iO)", event.type, py_size);
        }
    }

    return Py_BuildValue("(i)", event.type);
error:
    ex = PyErr_GetRaisedException();
    if (emath_api){ EMathApi_Release(); }
    PyErr_SetRaisedException(ex);
    return 0;
}

static PyObject *
show_cursor(PyObject *module, PyObject *unused)
{
    if (!SDL_ShowCursor()){ RAISE_SDL_ERROR(); }
    Py_RETURN_NONE;
error:
    return 0;
}

static PyObject *
hide_cursor(PyObject *module, PyObject *unused)
{
    if (!SDL_HideCursor()){ RAISE_SDL_ERROR(); }
    Py_RETURN_NONE;
error:
    return 0;
}

static PyMethodDef module_PyMethodDef[] = {
    {"initialize_sdl", initialize_sdl, METH_NOARGS, 0},
    {"deinitialize_sdl", deinitialize_sdl, METH_NOARGS, 0},
    {"create_sdl_window", create_sdl_window, METH_NOARGS, 0},
    {"delete_sdl_window", delete_sdl_window, METH_O, 0},
    {"show_sdl_window", show_sdl_window, METH_O, 0},
    {"hide_sdl_window", hide_sdl_window, METH_O, 0},
    {"set_sdl_window_size", (PyCFunction)set_sdl_window_size, METH_FASTCALL, 0},
    {"center_sdl_window", center_sdl_window, METH_O, 0},
    {"swap_sdl_window", (PyCFunction)swap_sdl_window, METH_FASTCALL, 0},
    {"enable_sdl_window_text_input", (PyCFunction)enable_sdl_window_text_input, METH_FASTCALL, 0},
    {"disable_sdl_window_text_input", disable_sdl_window_text_input, METH_O, 0},
    {"create_sdl_gl_context", create_sdl_gl_context, METH_O, 0},
    {"delete_sdl_gl_context", delete_sdl_gl_context, METH_O, 0},
    {"get_gl_attrs", get_gl_attrs, METH_NOARGS, 0},
    {"set_clipboard", set_clipboard, METH_O, 0},
    {"get_clipboard", get_clipboard, METH_NOARGS, 0},
    {"clear_sdl_events", clear_sdl_events, METH_NOARGS, 0},
    {"push_sdl_event", (PyCFunction)push_sdl_event, METH_FASTCALL, 0},
    {"get_sdl_event", get_sdl_event, METH_NOARGS, 0},
    {"show_cursor", get_clipboard, METH_NOARGS, 0},
    {"hide_cursor", get_sdl_event, METH_NOARGS, 0},
    {0},
};

static struct PyModuleDef module_PyModuleDef = {
    PyModuleDef_HEAD_INIT,
    "eplatform._eplatform",
    0,
    sizeof(ModuleState),
    module_PyMethodDef,
};

PyMODINIT_FUNC
PyInit__eplatform()
{
    PyObject *module = PyModule_Create(&module_PyModuleDef);
    if (!module){ return 0; }

    if (PyState_AddModule(module, &module_PyModuleDef) == -1)
    {
        Py_DECREF(module);
        return 0;
    }
    {
        PyObject *r = reset_module_state(module, 0);
        if (!r)
        {
            Py_DECREF(module);
            return 0;
        }
        Py_DECREF(r);
    }

#define ADD_CONSTANT(n)\
    {\
        PyObject *constant = PyLong_FromLong(n);\
        if (!constant){ return 0; }\
        if (PyModule_AddObject(module, #n, constant) != 0)\
        {\
            Py_DECREF(constant);\
            return 0;\
        }\
    }

    ADD_CONSTANT(SDL_EVENT_QUIT);
    ADD_CONSTANT(SDL_EVENT_MOUSE_MOTION);
    ADD_CONSTANT(SDL_EVENT_MOUSE_WHEEL);
    ADD_CONSTANT(SDL_EVENT_MOUSE_BUTTON_DOWN);
    ADD_CONSTANT(SDL_EVENT_MOUSE_BUTTON_UP);
    ADD_CONSTANT(SDL_EVENT_KEY_DOWN);
    ADD_CONSTANT(SDL_EVENT_KEY_UP);
    ADD_CONSTANT(SDL_EVENT_TEXT_INPUT);
    ADD_CONSTANT(SDL_EVENT_WINDOW_RESIZED);
    ADD_CONSTANT(SDL_EVENT_WINDOW_SHOWN);
    ADD_CONSTANT(SDL_EVENT_WINDOW_HIDDEN);

    ADD_CONSTANT(SDL_BUTTON_LEFT);
    ADD_CONSTANT(SDL_BUTTON_MIDDLE);
    ADD_CONSTANT(SDL_BUTTON_RIGHT);
    ADD_CONSTANT(SDL_BUTTON_X1);
    ADD_CONSTANT(SDL_BUTTON_X2);

    // number
    ADD_CONSTANT(SDL_SCANCODE_0);
    ADD_CONSTANT(SDL_SCANCODE_1);
    ADD_CONSTANT(SDL_SCANCODE_2);
    ADD_CONSTANT(SDL_SCANCODE_3);
    ADD_CONSTANT(SDL_SCANCODE_4);
    ADD_CONSTANT(SDL_SCANCODE_5);
    ADD_CONSTANT(SDL_SCANCODE_6);
    ADD_CONSTANT(SDL_SCANCODE_7);
    ADD_CONSTANT(SDL_SCANCODE_8);
    ADD_CONSTANT(SDL_SCANCODE_9);
    // function
    ADD_CONSTANT(SDL_SCANCODE_F1);
    ADD_CONSTANT(SDL_SCANCODE_F2);
    ADD_CONSTANT(SDL_SCANCODE_F3);
    ADD_CONSTANT(SDL_SCANCODE_F4);
    ADD_CONSTANT(SDL_SCANCODE_F5);
    ADD_CONSTANT(SDL_SCANCODE_F6);
    ADD_CONSTANT(SDL_SCANCODE_F7);
    ADD_CONSTANT(SDL_SCANCODE_F8);
    ADD_CONSTANT(SDL_SCANCODE_F9);
    ADD_CONSTANT(SDL_SCANCODE_F10);
    ADD_CONSTANT(SDL_SCANCODE_F11);
    ADD_CONSTANT(SDL_SCANCODE_F12);
    ADD_CONSTANT(SDL_SCANCODE_F13);
    ADD_CONSTANT(SDL_SCANCODE_F14);
    ADD_CONSTANT(SDL_SCANCODE_F15);
    ADD_CONSTANT(SDL_SCANCODE_F16);
    ADD_CONSTANT(SDL_SCANCODE_F17);
    ADD_CONSTANT(SDL_SCANCODE_F18);
    ADD_CONSTANT(SDL_SCANCODE_F19);
    ADD_CONSTANT(SDL_SCANCODE_F20);
    ADD_CONSTANT(SDL_SCANCODE_F21);
    ADD_CONSTANT(SDL_SCANCODE_F22);
    ADD_CONSTANT(SDL_SCANCODE_F23);
    ADD_CONSTANT(SDL_SCANCODE_F24);
    // letters
    ADD_CONSTANT(SDL_SCANCODE_A);
    ADD_CONSTANT(SDL_SCANCODE_B);
    ADD_CONSTANT(SDL_SCANCODE_C);
    ADD_CONSTANT(SDL_SCANCODE_D);
    ADD_CONSTANT(SDL_SCANCODE_E);
    ADD_CONSTANT(SDL_SCANCODE_F);
    ADD_CONSTANT(SDL_SCANCODE_G);
    ADD_CONSTANT(SDL_SCANCODE_H);
    ADD_CONSTANT(SDL_SCANCODE_I);
    ADD_CONSTANT(SDL_SCANCODE_J);
    ADD_CONSTANT(SDL_SCANCODE_K);
    ADD_CONSTANT(SDL_SCANCODE_L);
    ADD_CONSTANT(SDL_SCANCODE_M);
    ADD_CONSTANT(SDL_SCANCODE_N);
    ADD_CONSTANT(SDL_SCANCODE_O);
    ADD_CONSTANT(SDL_SCANCODE_P);
    ADD_CONSTANT(SDL_SCANCODE_Q);
    ADD_CONSTANT(SDL_SCANCODE_R);
    ADD_CONSTANT(SDL_SCANCODE_S);
    ADD_CONSTANT(SDL_SCANCODE_T);
    ADD_CONSTANT(SDL_SCANCODE_U);
    ADD_CONSTANT(SDL_SCANCODE_V);
    ADD_CONSTANT(SDL_SCANCODE_W);
    ADD_CONSTANT(SDL_SCANCODE_X);
    ADD_CONSTANT(SDL_SCANCODE_Y);
    ADD_CONSTANT(SDL_SCANCODE_Z);
    // symbols/operators
    ADD_CONSTANT(SDL_SCANCODE_APOSTROPHE);
    ADD_CONSTANT(SDL_SCANCODE_BACKSLASH);
    ADD_CONSTANT(SDL_SCANCODE_COMMA);
    ADD_CONSTANT(SDL_SCANCODE_DECIMALSEPARATOR);
    ADD_CONSTANT(SDL_SCANCODE_EQUALS);
    ADD_CONSTANT(SDL_SCANCODE_GRAVE);
    ADD_CONSTANT(SDL_SCANCODE_LEFTBRACKET);
    ADD_CONSTANT(SDL_SCANCODE_MINUS);
    ADD_CONSTANT(SDL_SCANCODE_NONUSBACKSLASH);
    ADD_CONSTANT(SDL_SCANCODE_NONUSHASH);
    ADD_CONSTANT(SDL_SCANCODE_PERIOD);
    ADD_CONSTANT(SDL_SCANCODE_RIGHTBRACKET);
    ADD_CONSTANT(SDL_SCANCODE_RSHIFT);
    ADD_CONSTANT(SDL_SCANCODE_SEMICOLON);
    ADD_CONSTANT(SDL_SCANCODE_SEPARATOR);
    ADD_CONSTANT(SDL_SCANCODE_SLASH);
    ADD_CONSTANT(SDL_SCANCODE_SPACE);
    ADD_CONSTANT(SDL_SCANCODE_TAB);
    ADD_CONSTANT(SDL_SCANCODE_THOUSANDSSEPARATOR);
    // actions
    ADD_CONSTANT(SDL_SCANCODE_AGAIN);
    ADD_CONSTANT(SDL_SCANCODE_ALTERASE);
    ADD_CONSTANT(SDL_SCANCODE_APPLICATION);
    ADD_CONSTANT(SDL_SCANCODE_BACKSPACE);
    ADD_CONSTANT(SDL_SCANCODE_CANCEL);
    ADD_CONSTANT(SDL_SCANCODE_CAPSLOCK);
    ADD_CONSTANT(SDL_SCANCODE_CLEAR);
    ADD_CONSTANT(SDL_SCANCODE_CLEARAGAIN);
    ADD_CONSTANT(SDL_SCANCODE_COPY);
    ADD_CONSTANT(SDL_SCANCODE_CRSEL);
    ADD_CONSTANT(SDL_SCANCODE_CURRENCYSUBUNIT);
    ADD_CONSTANT(SDL_SCANCODE_CURRENCYUNIT);
    ADD_CONSTANT(SDL_SCANCODE_CUT);
    ADD_CONSTANT(SDL_SCANCODE_DELETE);
    ADD_CONSTANT(SDL_SCANCODE_END);
    ADD_CONSTANT(SDL_SCANCODE_ESCAPE);
    ADD_CONSTANT(SDL_SCANCODE_EXECUTE);
    ADD_CONSTANT(SDL_SCANCODE_EXSEL);
    ADD_CONSTANT(SDL_SCANCODE_FIND);
    ADD_CONSTANT(SDL_SCANCODE_HELP);
    ADD_CONSTANT(SDL_SCANCODE_HOME);
    ADD_CONSTANT(SDL_SCANCODE_INSERT);
    ADD_CONSTANT(SDL_SCANCODE_LALT);
    ADD_CONSTANT(SDL_SCANCODE_LCTRL);
    ADD_CONSTANT(SDL_SCANCODE_LGUI);
    ADD_CONSTANT(SDL_SCANCODE_LSHIFT);
    ADD_CONSTANT(SDL_SCANCODE_MENU);
    ADD_CONSTANT(SDL_SCANCODE_MODE);
    ADD_CONSTANT(SDL_SCANCODE_NUMLOCKCLEAR);
    ADD_CONSTANT(SDL_SCANCODE_OPER);
    ADD_CONSTANT(SDL_SCANCODE_OUT);
    ADD_CONSTANT(SDL_SCANCODE_PAGEDOWN);
    ADD_CONSTANT(SDL_SCANCODE_PAGEUP);
    ADD_CONSTANT(SDL_SCANCODE_PASTE);
    ADD_CONSTANT(SDL_SCANCODE_PAUSE);
    ADD_CONSTANT(SDL_SCANCODE_POWER);
    ADD_CONSTANT(SDL_SCANCODE_PRINTSCREEN);
    ADD_CONSTANT(SDL_SCANCODE_PRIOR);
    ADD_CONSTANT(SDL_SCANCODE_RALT);
    ADD_CONSTANT(SDL_SCANCODE_RCTRL);
    ADD_CONSTANT(SDL_SCANCODE_RETURN);
    ADD_CONSTANT(SDL_SCANCODE_RETURN2);
    ADD_CONSTANT(SDL_SCANCODE_RGUI);
    ADD_CONSTANT(SDL_SCANCODE_SCROLLLOCK);
    ADD_CONSTANT(SDL_SCANCODE_SELECT);
    ADD_CONSTANT(SDL_SCANCODE_SLEEP);
    ADD_CONSTANT(SDL_SCANCODE_STOP);
    ADD_CONSTANT(SDL_SCANCODE_SYSREQ);
    ADD_CONSTANT(SDL_SCANCODE_UNDO);
    ADD_CONSTANT(SDL_SCANCODE_VOLUMEDOWN);
    ADD_CONSTANT(SDL_SCANCODE_VOLUMEUP);
    ADD_CONSTANT(SDL_SCANCODE_MUTE);
    // media
    ADD_CONSTANT(SDL_SCANCODE_MEDIA_SELECT);
    ADD_CONSTANT(SDL_SCANCODE_MEDIA_EJECT);
    ADD_CONSTANT(SDL_SCANCODE_MEDIA_FAST_FORWARD);
    ADD_CONSTANT(SDL_SCANCODE_MEDIA_NEXT_TRACK);
    ADD_CONSTANT(SDL_SCANCODE_MEDIA_PLAY);
    ADD_CONSTANT(SDL_SCANCODE_MEDIA_PREVIOUS_TRACK);
    ADD_CONSTANT(SDL_SCANCODE_MEDIA_REWIND);
    ADD_CONSTANT(SDL_SCANCODE_MEDIA_STOP);
    // ac
    ADD_CONSTANT(SDL_SCANCODE_AC_BACK);
    ADD_CONSTANT(SDL_SCANCODE_AC_BOOKMARKS);
    ADD_CONSTANT(SDL_SCANCODE_AC_FORWARD);
    ADD_CONSTANT(SDL_SCANCODE_AC_HOME);
    ADD_CONSTANT(SDL_SCANCODE_AC_REFRESH);
    ADD_CONSTANT(SDL_SCANCODE_AC_SEARCH);
    ADD_CONSTANT(SDL_SCANCODE_AC_STOP);
    // arrows
    ADD_CONSTANT(SDL_SCANCODE_DOWN);
    ADD_CONSTANT(SDL_SCANCODE_LEFT);
    ADD_CONSTANT(SDL_SCANCODE_RIGHT);
    ADD_CONSTANT(SDL_SCANCODE_UP);
    // international
    ADD_CONSTANT(SDL_SCANCODE_INTERNATIONAL1);
    ADD_CONSTANT(SDL_SCANCODE_INTERNATIONAL2);
    ADD_CONSTANT(SDL_SCANCODE_INTERNATIONAL3);
    ADD_CONSTANT(SDL_SCANCODE_INTERNATIONAL4);
    ADD_CONSTANT(SDL_SCANCODE_INTERNATIONAL5);
    ADD_CONSTANT(SDL_SCANCODE_INTERNATIONAL6);
    ADD_CONSTANT(SDL_SCANCODE_INTERNATIONAL7);
    ADD_CONSTANT(SDL_SCANCODE_INTERNATIONAL8);
    ADD_CONSTANT(SDL_SCANCODE_INTERNATIONAL9);
    // numpad numbers
    ADD_CONSTANT(SDL_SCANCODE_KP_0);
    ADD_CONSTANT(SDL_SCANCODE_KP_00);
    ADD_CONSTANT(SDL_SCANCODE_KP_000);
    ADD_CONSTANT(SDL_SCANCODE_KP_1);
    ADD_CONSTANT(SDL_SCANCODE_KP_2);
    ADD_CONSTANT(SDL_SCANCODE_KP_3);
    ADD_CONSTANT(SDL_SCANCODE_KP_4);
    ADD_CONSTANT(SDL_SCANCODE_KP_5);
    ADD_CONSTANT(SDL_SCANCODE_KP_6);
    ADD_CONSTANT(SDL_SCANCODE_KP_7);
    ADD_CONSTANT(SDL_SCANCODE_KP_8);
    ADD_CONSTANT(SDL_SCANCODE_KP_9);
    // numpad letters
    ADD_CONSTANT(SDL_SCANCODE_KP_A);
    ADD_CONSTANT(SDL_SCANCODE_KP_B);
    ADD_CONSTANT(SDL_SCANCODE_KP_C);
    ADD_CONSTANT(SDL_SCANCODE_KP_D);
    ADD_CONSTANT(SDL_SCANCODE_KP_E);
    ADD_CONSTANT(SDL_SCANCODE_KP_F);
    // numpad symbols/operators
    ADD_CONSTANT(SDL_SCANCODE_KP_AMPERSAND);
    ADD_CONSTANT(SDL_SCANCODE_KP_AT);
    ADD_CONSTANT(SDL_SCANCODE_KP_COLON);
    ADD_CONSTANT(SDL_SCANCODE_KP_COMMA);
    ADD_CONSTANT(SDL_SCANCODE_KP_DBLAMPERSAND);
    ADD_CONSTANT(SDL_SCANCODE_KP_DBLVERTICALBAR);
    ADD_CONSTANT(SDL_SCANCODE_KP_DECIMAL);
    ADD_CONSTANT(SDL_SCANCODE_KP_DIVIDE);
    ADD_CONSTANT(SDL_SCANCODE_KP_ENTER);
    ADD_CONSTANT(SDL_SCANCODE_KP_EQUALS);
    ADD_CONSTANT(SDL_SCANCODE_KP_EQUALSAS400);
    ADD_CONSTANT(SDL_SCANCODE_KP_EXCLAM);
    ADD_CONSTANT(SDL_SCANCODE_KP_GREATER);
    ADD_CONSTANT(SDL_SCANCODE_KP_HASH);
    ADD_CONSTANT(SDL_SCANCODE_KP_LEFTBRACE);
    ADD_CONSTANT(SDL_SCANCODE_KP_LEFTPAREN);
    ADD_CONSTANT(SDL_SCANCODE_KP_LESS);
    ADD_CONSTANT(SDL_SCANCODE_KP_MINUS);
    ADD_CONSTANT(SDL_SCANCODE_KP_MULTIPLY);
    ADD_CONSTANT(SDL_SCANCODE_KP_PERCENT);
    ADD_CONSTANT(SDL_SCANCODE_KP_PERIOD);
    ADD_CONSTANT(SDL_SCANCODE_KP_PLUS);
    ADD_CONSTANT(SDL_SCANCODE_KP_PLUSMINUS);
    ADD_CONSTANT(SDL_SCANCODE_KP_POWER);
    ADD_CONSTANT(SDL_SCANCODE_KP_RIGHTBRACE);
    ADD_CONSTANT(SDL_SCANCODE_KP_RIGHTPAREN);
    ADD_CONSTANT(SDL_SCANCODE_KP_SPACE);
    ADD_CONSTANT(SDL_SCANCODE_KP_TAB);
    ADD_CONSTANT(SDL_SCANCODE_KP_VERTICALBAR);
    ADD_CONSTANT(SDL_SCANCODE_KP_XOR);
    // numpad actions
    ADD_CONSTANT(SDL_SCANCODE_KP_BACKSPACE);
    ADD_CONSTANT(SDL_SCANCODE_KP_BINARY);
    ADD_CONSTANT(SDL_SCANCODE_KP_CLEAR);
    ADD_CONSTANT(SDL_SCANCODE_KP_CLEARENTRY);
    ADD_CONSTANT(SDL_SCANCODE_KP_HEXADECIMAL);
    ADD_CONSTANT(SDL_SCANCODE_KP_OCTAL);
    // memory
    ADD_CONSTANT(SDL_SCANCODE_KP_MEMADD);
    ADD_CONSTANT(SDL_SCANCODE_KP_MEMCLEAR);
    ADD_CONSTANT(SDL_SCANCODE_KP_MEMDIVIDE);
    ADD_CONSTANT(SDL_SCANCODE_KP_MEMMULTIPLY);
    ADD_CONSTANT(SDL_SCANCODE_KP_MEMRECALL);
    ADD_CONSTANT(SDL_SCANCODE_KP_MEMSTORE);
    ADD_CONSTANT(SDL_SCANCODE_KP_MEMSUBTRACT);
    // language
    ADD_CONSTANT(SDL_SCANCODE_LANG1);
    ADD_CONSTANT(SDL_SCANCODE_LANG2);
    ADD_CONSTANT(SDL_SCANCODE_LANG3);
    ADD_CONSTANT(SDL_SCANCODE_LANG4);
    ADD_CONSTANT(SDL_SCANCODE_LANG5);
    ADD_CONSTANT(SDL_SCANCODE_LANG6);
    ADD_CONSTANT(SDL_SCANCODE_LANG7);
    ADD_CONSTANT(SDL_SCANCODE_LANG8);
    ADD_CONSTANT(SDL_SCANCODE_LANG9);

    return module;
}