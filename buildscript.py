from __future__ import annotations

__all__ = ()

# setuptools
from setuptools import Distribution
from setuptools import Extension
from setuptools.command.build_ext import build_ext

# python
import os
from pathlib import Path
from platform import system
import shutil
import sys

_coverage_compile_args: list[str] = []
_coverage_links_args: list[str] = []
if os.environ.get("EPLATFORM_BUILD_WITH_COVERAGE", "0") == "1":
    if system() == "Windows":
        print("Cannot build with coverage on windows.")
        sys.exit(1)
    _coverage_compile_args = ["-fprofile-arcs", "-ftest-coverage", "-O0"]
    _coverage_links_args = ["-fprofile-arcs"]

libraries: list[str] = []
library_dirs: list[str] = []
extra_link_args: list[str] = []
define_macros: list[tuple[str, None]] = []
if system() == "Windows":
    libraries.append("SDL3")
    library_dirs.append("vendor/SDL/Release")
elif system() == "Darwin":
    pass
else:
    pass

_eplatform = Extension(
    "eplatform._eplatform",
    library_dirs=library_dirs,
    libraries=libraries,
    include_dirs=["src/eplatform", "vendor/SDL/include", "vendor/emath/include"],
    sources=["src/eplatform/_eplatform.c"],
    extra_compile_args=_coverage_compile_args,
    extra_link_args=_coverage_links_args + extra_link_args,
    define_macros=define_macros,
)

"""
def _build_sdl() -> None:
    subprocess.run(["cmake", "."], cwd="vendor/SDL", check=True)
    if system() == "Windows":
        from setuptools.msvc import EnvironmentInfo
        ms_env = EnvironmentInfo(machine())
        env = os.environ.copy()
        env["PATH"] = ";".join((*ms_env.VCTools, *env["PATH"].split(";")))
        subprocess.run(
            ["msbuild", "SDL3-shared.vcxproj", "/p:Configuration=Release"],
            cwd="vendor/SDL",
            check=True,
            env=env
        )
        shutil.copyfile("vendor/SDL/Release/SDL3.dll", "SDL3.dll")
    else:
        raise RuntimeError("idk how to build SDL")
"""


def _build() -> None:
    cmd = build_ext(Distribution({"name": "extended", "ext_modules": [_eplatform]}))
    cmd.ensure_finalized()
    cmd.run()
    for output in cmd.get_outputs():
        dest = str(Path("src/eplatform/") / Path(output).name)
        print(f"copying {output} to {dest}...")
        shutil.copyfile(output, dest)


if __name__ == "__main__":
    _build()
