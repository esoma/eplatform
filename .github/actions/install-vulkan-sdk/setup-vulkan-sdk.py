import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from platform import system

VULKAN_SDK = Path("vulkan-sdk").absolute()

with open(os.environ["GITHUB_ENV"], "w", encoding="utf-8") as env:
    print(f"VULKAN_SDK={VULKAN_SDK}", file=env)
    print(f"VK_SDK_PATH={VULKAN_SDK}", file=env)

    if system() == "Windows":
        with tempfile.TemporaryDirectory() as temp_dir:
            shutil.copyfile(str(VULKAN_SDK / "install.exe"), Path(temp_dir) / "install.exe")
            (VULKAN_SDK / "install.exe").unlink()
            subprocess.run(
                [
                    str(Path(temp_dir) / "install.exe"),
                    "--root",
                    str(VULKAN_SDK),
                    "--accept-licenses",
                    "--confirm-command",
                    "install",
                ],
                check=True,
            )

    if system() != "Windows":
        try:
            VK_ADD_LAYER_PATH = ":" + os.environ["VK_ADD_LAYER_PATH"]
        except KeyError:
            VK_ADD_LAYER_PATH = ""
        print(
            f"VK_ADD_LAYER_PATH={VULKAN_SDK / 'share/vulkan/explicit_layer.d'}{VK_ADD_LAYER_PATH}",
            file=env,
        )

    if system() == "Linux":
        try:
            LD_LIBRARY_PATH = ":" + os.environ["LD_LIBRARY_PATH"]
        except KeyError:
            LD_LIBRARY_PATH = ""
        print(f"LD_LIBRARY_PATH={VULKAN_SDK / 'lib'}{LD_LIBRARY_PATH}", file=env)

    if system() == "Darwin":
        print(f"SDL_VULKAN_LIBRARY={VULKAN_SDK / 'lib/libvulkan.1.dylib'}", file=env)
        try:
            DYLD_LIBRARY_PATH = ":" + os.environ["DYLD_LIBRARY_PATH"]
        except KeyError:
            DYLD_LIBRARY_PATH = ""
        print(f"DYLD_LIBRARY_PATH={VULKAN_SDK / 'lib'}{DYLD_LIBRARY_PATH}", file=env)


with open(os.environ["GITHUB_OUTPUT"], "w", encoding="utf-8") as output:
    print(f"path={VULKAN_SDK}", file=output)
