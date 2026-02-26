import os
import os.path
import shutil
import subprocess
import sys
from pathlib import Path
from platform import system
from tempfile import TemporaryDirectory
from urllib.request import Request
from urllib.request import urlopen

SDK_VERSION = sys.argv[1]

if system() == "Windows":
    SDK_URI = f"https://sdk.lunarg.com/sdk/download/{SDK_VERSION}/windows/vulkan_sdk.exe"
elif system() == "Linux":
    SDK_URI = f"https://sdk.lunarg.com/sdk/download/{SDK_VERSION}/linux/vulkan_sdk.tar.xz"
elif system() == "Darwin":
    SDK_URI = f"https://sdk.lunarg.com/sdk/download/{SDK_VERSION}/mac/vulkan_sdk.zip"
else:
    raise RuntimeError(f"unexpected system: {system()}")

print(f"downloading vulkan sdk: {SDK_URI}")
request = Request(SDK_URI)
request.add_header("User-Agent", "Python")
with TemporaryDirectory() as sdk_dir:
    sdk_file_name = Path(sdk_dir) / "sdk"
    with urlopen(request) as response:
        with open(sdk_file_name, "wb") as sdk_file:
            sdk_file.write(response.read())

    os.mkdir("vulkan-sdk")

    if system() == "Windows":
        shutil.copyfile(sdk_file_name, "vulkan-sdk/install.exe")
    elif system() == "Linux":
        subprocess.run(
            [
                "tar",
                "-xf",
                sdk_file_name,
                "-C",
                "vulkan-sdk",
                "--strip-components",
                "2",
                f"{SDK_VERSION}/x86_64",
            ],
            check=True,
        )
    elif system() == "Darwin":
        with TemporaryDirectory() as unzip_dir:
            subprocess.run(["unzip", sdk_file_name, "-d", unzip_dir])
            with TemporaryDirectory() as install_dir:
                subprocess.run(
                    [
                        Path(unzip_dir)
                        / f"vulkansdk-macOS-{SDK_VERSION}.app/Contents/MacOS/vulkansdk-macOS-{SDK_VERSION}",
                        "--root",
                        install_dir,
                        "--accept-licenses",
                        "--confirm-command",
                        "install",
                    ],
                    check=True,
                )
                subprocess.run(["cp", "-R", f"{install_dir}/macOS/.", "vulkan-sdk"], check=True)

    else:
        raise RuntimeError(f"unexpected system: {system()}")
