from gtts import gTTS
import bpy
from bpy import context
import os

bl_info = {
    "name": "Text To Speech",
    "description": "turns text into speech",
    "author": "Mark Lagana",
    "version": (1, 0),
    "blender": (2, 82, 0),
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

class TextToSpeech(bpy.types.Panel):
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_label = 'Text to speech'
    bl_category = 'Text To Speech'
    
    def draw(self, context):
        layout = self.layout
        layout.operator('custom.speak', text = 'speak')
        layout.prop(context.scene.custom_props, 'string_field')

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
          
        bpy.ops.sequencer.sound_strip_add(  filepath=output_dir + str(count) + ".mp3",
                                            frame_start=bpy.context.scene.frame_current,
                                            channel=2)
        count += 1
        self.report({'INFO'}, output_dir + str(count) + ".mp3 created")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(CustomPropertyGroup)
    bpy.types.Scene.custom_props = bpy.props.PointerProperty(type=CustomPropertyGroup)
    bpy.utils.register_class(TextToSpeech)
    bpy.utils.register_class(TextToSpeechOperator)


def unregister():
    del bpy.types.Scene.custom_props
    bpy.utils.register_class(CustomPropertyGroup)
    bpy.utils.unregister_class(TextToSpeech)
    bpy.utils.unregister_class(TextToSpeechOperator)     

if __name__ == '__main__':
    register()
