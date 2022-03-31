import sys
import os
from sys import platform
import subprocess
from pathlib import Path
import bpy

from .installers import osx
from .installers import linux
from .installers import windows
from .installers import other

def install():

    print(f"attempting gtts install on {platform} blender version {bpy.app.version}")

    if platform.startswith("linux"):
        linux.install()
    elif platform == "win32":
        windows.install()
    elif platform == "darwin":
        osx.install()
    else:
        other.install()