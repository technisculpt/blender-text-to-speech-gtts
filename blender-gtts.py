from gtts import gTTS
import bpy
from bpy import context
import os
from bpy_extras.io_utils import ImportHelper
from pathlib import Path
from bpy.props import StringProperty, CollectionProperty
from bpy.types import Operator

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
global count
count = 0

if os.name == 'nt':
    output_dir = r'C:\\tmp\\'
else:
    output_dir = r'/tmp/'

class CustomPropertyGroup(bpy.types.PropertyGroup):
    string_field: bpy.props.StringProperty(name='text')

class ImportTranscript(Operator, ImportHelper):
    bl_idname = "_import.txt_file"
    bl_label = "Import Some Data"

    # ImportHelper mixin class uses this
    filename_ext = ".txt"

    filter_glob = StringProperty(
            default="*.txt",
            options={'HIDDEN'},
            )

    filename = StringProperty(maxlen=1024)
    directory = StringProperty(maxlen=1024)

    def execute(self, context):

        #f = Path(bpy.path.abspath(self.filepath)) # make a path object of abs path
        f = Path(r'C:\Users\marco\blender-gtts\transcript-example.txt')
        if f.exists():
            text = f.read_text()
            lines = text.split("\n")
            print(lines)
        return {'FINISHED'}

class TextToSpeech(bpy.types.Panel):
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_label = 'Text to speech'
    bl_category = 'Text To Speech'
    
    def draw(self, context):
        layout = self.layout
        layout.operator('custom.speak', text = 'speak')
        layout.prop(context.scene.custom_props, 'string_field')
        layout.operator('custom.load', text = 'load file')

class TextToSpeechOperator(bpy.types.Operator):
    bl_idname = 'custom.speak'
    bl_label = 'speak op'
    bl_options = {'INTERNAL'}
  
    @classmethod
    def poll(cls, context):
        return context.object is not None
    
    def execute(self, context):
        global count
        scene = context.scene
        ttmp3 = gTTS(text=context.scene.custom_props.string_field, lang="en", tld="com.au")
        ttmp3.save(output_dir + str(count) + ".mp3")
        scene = context.scene
        
        if not scene.sequence_editor:
          scene.sequence_editor_create()
        seq = scene.sequence_editor

        bpy.ops.sequencer.sound_strip_add(  filepath=output_dir + str(count) + ".mp3",
                                            frame_start=bpy.context.scene.frame_current,
                                            channel=2)
        for strip in seq.sequences_all:
            #print(strip.name)
            print(strip.frame_start)
            #strip.show_waveform = True

        count += 1
        self.report({'INFO'}, output_dir + str(count) + ".mp3 created")
        return {'FINISHED'}

class LoadFileOperator(bpy.types.Operator):
    bl_idname = 'custom.load'
    bl_label = 'load op'
    bl_options = {'INTERNAL'}
  
    @classmethod
    def poll(cls, context):
        return context.object is not None
    
    def execute(self, context):
        bpy.ops._import.txt_file('INVOKE_DEFAULT')
        self.report({'INFO'}, "done")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(CustomPropertyGroup)
    bpy.types.Scene.custom_props = bpy.props.PointerProperty(type=CustomPropertyGroup)
    bpy.utils.register_class(TextToSpeech)
    bpy.utils.register_class(TextToSpeechOperator)
    bpy.utils.register_class(LoadFileOperator)
    bpy.utils.register_class(ImportTranscript)

def unregister():
    del bpy.types.Scene.custom_props
    bpy.utils.register_class(CustomPropertyGroup)
    bpy.utils.unregister_class(TextToSpeech)
    bpy.utils.unregister_class(TextToSpeechOperator)     
    bpy.utils.unregister_class(LoadFileOperator)  
    bpy.utils.unregister_class(ImportTranscript)

if __name__ == '__main__':
    register()


'''
strip.
          animation_offset_end
          animation_offset_start
          as_pointer(
          bl_rna
          bl_rna_get_subclass(
          bl_rna_get_subclass_py(
          blend_alpha
          blend_type
          channel
          driver_add(
          driver_remove(
          effect_fader
          frame_duration
          frame_final_duration
          frame_final_end
          frame_final_start
          frame_offset_end
          frame_offset_start
          frame_start
          frame_still_end
          frame_still_start
          get(
          id_data
          invalidate_cache(
          is_property_hidden(
          is_property_overridable_library(
          is_property_readonly(
          is_property_set(
          items(
          keyframe_delete(
          keyframe_insert(
          keys(
          lock
          modifiers
          move_to_meta(
          mute
          name
          override_cache_settings
          pan
          path_from_id(
          path_resolve(
          pitch
          pop(
          property_overridable_library_set(
          property_unset(
          rna_type
          select
          select_left_handle
          select_right_handle
          show_waveform
          sound
          speed_factor
          strip_elem_from_frame(
          swap(
          type
          type_recast(
          update(
          use_cache_composite
          use_cache_preprocessed
          use_cache_raw
          use_default_fade
          use_linear_modifiers
          values(
          volume
'''