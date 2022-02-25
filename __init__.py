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
    py_exec = bpy.app.binary_path_python
    subprocess.call([str(py_exec), "-m", "ensurepip", "--user"])
    subprocess.call([str(py_exec), "-m", "pip", "install", "--upgrade", "pip"])
    subprocess.call([str(py_exec),"-m", "pip", "install", "--user", "gtts"])
    
    try:
        import gtts
    except ModuleNotFoundError:
        print("Error installing gtts. Try restarting Blender. If using Windows open Blender as administrator (for initial install)")

from numbers import Number
from re import T
import bpy
from bpy.props import StringProperty, CollectionProperty

# append dir to path for dev, for prod use from . import module
import sys
dir = r'/home/magag/text_to_speech'
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
