import subprocess
from pathlib import Path
import os
import sys
import bpy

def install():

    if bpy.app.version < (2, 92, 0):
        py_exec = bpy.app.binary_path_python
        subprocess.call([str(py_exec), "-m", "ensurepip", "--user"])
        subprocess.call([str(py_exec), "-m", "pip", "install", "--upgrade", "pip"])
        subprocess.call([str(py_exec),"-m", "pip", "install", "--user", "gtts"])
    else:
        py_exec = str(sys.executable)
        lib = os.path.join(Path(py_exec).parent.parent, 'lib', 'python3.10')
        subprocess.call([py_exec, "-m", "ensurepip", "--user" ])
        subprocess.call([py_exec, "-m", "pip", "install", "--upgrade", "pip" ])
        subprocess.call([py_exec,"-m", "pip", "install", f"--target={str(lib)}", "gtts"])
    try:
        import gtts
        print("gtts installed")
    except PermissionError:
        print("permission error")
    except:
        print("Error installing gtts")