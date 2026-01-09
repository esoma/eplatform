import os
import os.path
import subprocess
import sys
from pathlib import Path
from platform import system
from tempfile import TemporaryDirectory
from urllib.request import urlretrieve

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
sdk_file_name, _ = urlretrieve(SDK_URI)

os.mkdir("vulkan-sdk")

if system() == "Windows":
    subprocess.run(
        [
            sdk_file_name,
            "--root",
            os.path.abspath("vulkan-sdk"),
            "--accept-licenses",
            "--confirm-command",
            "install",
        ],
        check=True,
    )
    SDK_PATH = str((Path("vulkan-sdk") / SDK_VERSION).absolute())
elif system() == "Linux":
    subprocess.run(["tar", "-xf", sdk_file_name, "-C", "vulkan-sdk"], check=True)
    SDK_PATH = str((Path("vulkan-sdk") / SDK_VERSION).absolute())
elif system() == "Darwin":
    with TemporaryDirectory() as unzip_dir:
        subprocess.run(["unzip", sdk_file_name, "-d", unzip_dir])
        subprocess.run(
            [
                "sudo",
                Path(unzip_dir) / f"Contents/MacOS/vulkansdk-macOS-{SDK_VERSION}",
                "--root",
                os.path.abspath("vulkan-sdk"),
                "--accept-licenses",
                "--confirm-command",
                "install",
            ],
            check=True,
        )
    SDK_PATH = str((Path("vulkan-sdk") / SDK_VERSION).absolute())
else:
    raise RuntimeError(f"unexpected system: {system()}")

with open(os.environ["GITHUB_ENV"], "w") as github_env:
    github_env.write(f"VULKAN_SDK={SDK_PATH}")
