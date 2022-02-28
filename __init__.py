bl_info = {
    "name": "Text To Speech",
    "description": "turns text into speech",
    "author": "Mark Lagana",
    "version": (1, 0),
    "blender": (2, 93, 4),
    "location": "SEQUENCE_EDITOR > UI > Text To Speech",
    "warning": "",
    "doc_url": "https://github.com/technisculpt/blender-gtts",
    "support": "TESTING",
    "category": "Sequencer",
}

try:
    import gtts

except ModuleNotFoundError:
    print("installing gtts...")
    import subprocess
    import bpy
    import os
    from pathlib import Path

    if bpy.app.version < (2, 92, 0):
        py_exec = bpy.app.binary_path_python
        subprocess.call([str(py_exec), "-m", "ensurepip", "--user"])
        subprocess.call([str(py_exec), "-m", "pip", "install", "--upgrade", "pip"])
        subprocess.call([str(py_exec),"-m", "pip", "install", "--user", "gtts"])
    else:
        import sys
        py_exec = str(sys.executable)
        lib = os.path.join(Path(py_exec).parent.parent, "lib")
        subprocess.call([py_exec, "-m", "ensurepip", "--user" ])
        subprocess.call([py_exec, "-m", "pip", "install", "--upgrade", "pip" ])
        subprocess.call([py_exec,"-m", "pip", "install", f"--target={str(lib)}", "gtts"])
        
        try:
            import gtts
        except PermissionError:
            print("to install, right click the Blender icon and run as Administrator")
        except:
            print("Error installing gtts")

from numbers import Number
from re import T
import bpy
import sys
import os

# append dir to path for dev, for prod use from . import module
dir = r'/home/magag/text_to_speech'
if os.name == 'nt':
    dir = r"C:\Users\marco\blender-text-to-speech"
sys.path.append(dir)

import operators
import ui
import importlib
importlib.reload(operators)
importlib.reload(ui)

classes = (
    ui.TextToSpeechSettings,
    ui.TextToSpeech_PT,
    operators.TextToSpeechOperator,
    operators.LoadFileOperator,
    operators.ExportFileOperator,
    operators.ImportTranscript,
    )


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.text_to_speech = bpy.props.PointerProperty(type=ui.TextToSpeechSettings)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.text_to_speech



if __name__ == '__main__':
    register()
    print("done")