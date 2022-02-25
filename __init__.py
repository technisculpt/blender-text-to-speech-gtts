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
        print("Error installing gtts. Try restarting Blender. If using Windows open Blender as administrator for install")

from numbers import Number
from re import T
import bpy
import os

from bpy.props import StringProperty, CollectionProperty

# append dir to path for dev, for prod use from . import module
import sys
dir = r'/home/magag/text_to_speech'
sys.path.append(dir)

import operators
import importlib
importlib.reload(operators)


class CustomPropertyGroup(bpy.types.PropertyGroup):

    string_field : bpy.props.StringProperty(name='text')

    pitch : bpy.props.FloatProperty(
        name="Pitch",
        description="Control pitch",
        default=1.0,
        min=0.1,
        max=10.0)

    accent_enumerator : bpy.props.EnumProperty(
                name = "",
                description = "accent options for speakers",
                items=[ ('0',"Australia",""),
                        ('1',"United Kingdom",""),
                        ('2',"Canada",""),
                        ('3',"India",""),
                        ('4',"Ireland",""),
                        ('5',"South Africa",""),
                        ('6',"French Canada",""),
                        ('7',"France",""),
                        ('8',"Brazil",""),
                        ('9',"Portugal",""),
                        ('10',"Mexico",""),
                        ('11',"Spain",""),
                        ('12',"Spain (US)","")])

class ExportOptions(bpy.types.PropertyGroup):

    mode_enumerator : bpy.props.EnumProperty(
                    name = "",
                    description = "export options for closed captions",
                    items=[('0',"txt",""),('1',"srt",""),('2',"sbv","")])

class TextToSpeech(bpy.types.Panel):
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_label = 'Text to speech'
    bl_category = 'Text To Speech'
    
    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text="Add Caption:")
        layout.prop(context.scene.custom_props, 'string_field')
        layout.operator('custom.speak', text = 'add caption')
        col = layout.column()
        col.label(text="Load Captions:")
        layout.operator('custom.load', text = 'load captions file')

        col = layout.column()
        col.label(text="Export Captions:")
        subrow = layout.row(align=True)
        subrow.prop(context.scene.export_options, 'mode_enumerator')
        subrow.operator('custom.export', text = 'export')

        col = layout.column()
        col.label(text="Accent:")
        subrow = layout.row(align=True)
        subrow.prop(context.scene.custom_props, 'accent_enumerator')
        subrow.prop(context.scene.custom_props, 'pitch')

def register():
    bpy.utils.register_class(CustomPropertyGroup)
    bpy.types.Scene.custom_props = bpy.props.PointerProperty(type=CustomPropertyGroup)
    bpy.utils.register_class(ExportOptions)
    bpy.types.Scene.export_options = bpy.props.PointerProperty(type=ExportOptions)
    bpy.utils.register_class(TextToSpeech)
    bpy.utils.register_class(operators.TextToSpeechOperator)
    bpy.utils.register_class(operators.LoadFileOperator)
    bpy.utils.register_class(operators.ExportFileOperator)
    bpy.utils.register_class(operators.ImportTranscript)

def unregister():
    del bpy.types.Scene.custom_props
    del bpy.types.Scene.export_options
    bpy.utils.unregister_class(CustomPropertyGroup)
    bpy.utils.unregister_class(TextToSpeech)
    bpy.utils.unregister_class(operators.TextToSpeechOperator)     
    bpy.utils.unregister_class(operators.LoadFileOperator)
    bpy.utils.unregister_class(operators.ImportTranscript)
    bpy.utils.unregister_class(operators.ExportFileOperator)
    bpy.utils.unregister_class(ExportOptions)

if __name__ == '__main__':
    register()
