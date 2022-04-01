from sys import platform
from pathlib import Path
import importlib
import bpy

from .installers import osx
from .installers import linux
from .installers import windows
from .installers import other
importlib.reload(osx)
importlib.reload(linux)
importlib.reload(windows)
importlib.reload(other)

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