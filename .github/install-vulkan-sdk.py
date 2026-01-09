import os
import subprocess
import sys
from pathlib import Path
from platform import system
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
            "install",
            "--root",
            os.abspath("vulkan-sdk"),
            "--accept-licenses",
            "--confirm-command",
        ]
    )
else:
    raise RuntimeError(f"unexpected system: {system()}")
