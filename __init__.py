from gtts import gTTS
import bpy
from bpy import context
import os


global count
count = 0

if os.name == 'nt':
    output_dir = r'C:\\tmp\\'
else:
    output_dir = r'/tmp/'

class TextToSpeech(bpy.types.Panel):
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_label = 'Text to speech'
    bl_context = 'objectmode'
    bl_category = 'View'
    
    def draw(self, context):
        layout = self.layout
        layout.operator('custom.speak', text = 'speak')
        layout.prop(context.scene.custom_props, 'string_field')

class TextToSpeechOperator(bpy.types.Operator):
    bl_idname = 'custom.speak'
    #this is the label that essentially is the text displayed on the button
    bl_label = 'speak op'
    bl_options = {'INTERNAL'}
  
    @classmethod
    def poll(cls, context):
        return context.object is not None
    
    def execute(self, context):
        global count
        ttmp3 = gTTS(text=context.scene.custom_props, lang="en", tld="com.au")
        ttmp3.save(output_dir + str(count) + ".mp3")
        count += 1
        scene = context.scene
        
        if not scene.sequence_editor:
          scene.sequence_editor_create()
          
        #Sequences.new_sound(name, filepath, channel, frame_start)    
        soundstrip = scene.sequence_editor.sequences.new_sound(str(count), output_dir + str(count) + ".mp3", 3, 1)
        self.report({'INFO'}, "FINISHED")
        return {'FINISHED'}

def register():
    bpy.utils.register_class(CustomPropertyGroup)
    bpy.types.Scene.custom_props = bpy.props.PointerProperty(type=CustomPropertyGroup)
    bpy.utils.register_class(TextToSpeech)
    bpy.utils.register_class(TextToSpeechOperator)


def unregister():
    del bpy.types.Scene.custom_props 
    bpy.utils.unregister_class(TextToSpeech)
    bpy.utils.unregister_class(TextToSpeechOperator)     

if __name__ == '__main__':
    register()
