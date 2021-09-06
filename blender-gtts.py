from numbers import Number
from re import T
from gtts import gTTS
import bpy
from bpy import context
import os
from bpy_extras.io_utils import ImportHelper
from pathlib import Path
from bpy.props import StringProperty, CollectionProperty
from bpy.types import Operator
from datetime import datetime

DEBUG = True

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

DEBUG = False

if os.name == 'nt':
    output_dir = r'C:\\tmp\\'
else:
    output_dir = r'/tmp/'

class Time():

    def __init__(self, hours, minutes, seconds, milliseconds):
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
        self.milliseconds = milliseconds

    def timeToStr(self):
        return (str(self.hours) + ' ' + str(self.minutes) + ' ' + str(self.seconds) + ' ' + str(self.milliseconds))

class Caption():

    def __init__(self, cc_type, name, text, start_time, end_time):
        self.cc_type = cc_type # 0 : default, 1 : person, 2 : event
        self.name = name
        self.text = text
        self.start_time = start_time
        self.end_time = end_time
        print(self.cc_type, self.name, self.text, self.start_time.timeToStr(), self.end_time.timeToStr())

class ClosedCaptionSet():

    captions = []
    people = []

    def __init__(self, text, filename):
        self.text = text
        self.filename = filename
        self.file_type = -1

        if self.filename[-3:len(self.filename)] == 'txt':
            
            print(".txt file detected")
            self.file_type = 0
            line_counter = 0
            cc_text = ""
            cc_type = 1

            for line in self.text:
                if len(line) > 0:
                    if line[0:2].find('>>') != -1: # person
                        cc_type = 1
                        cc_name = line[2:len(line)].split(":")[0]
                        text_tmp = line[2:len(line)].split(":")[1]
                        cc_text = text_tmp[1:len(text_tmp)]
                        
                        newPerson = True
                        for person in self.people:
                            if person == cc_name:
                                newPerson = False
                                break
                        
                        if newPerson:
                            self.people.append(cc_name)

                    elif line[0] == '[': # event
                        cc_type = 2
                        cc_name = ''
                        cc_text = line.split('[')[1].split(']')[0]
                    
                    else: # plain text line

                        if len(cc_text) == 0: # no previous line
                            cc_name = "noname"
                            cc_type = 0
                            cc_text = line

                        else: # second line
                            cc_text += " " + line
                
                else: # len(line == 0) equivalent of '\n'
                    self.captions.append( Caption(cc_type, cc_name, cc_text, Time(-1, -1, -1, -1), Time(-1, -1, -1, -1)) )
                    cc_text = ""

                line_counter += 1
                if line_counter == len(self.text): # on exit
                    if len(cc_text) > 0:
                        self.captions.append( Caption(cc_type, cc_name, cc_text, Time(-1, -1, -1, -1), Time(-1, -1, -1, -1)) )
            
        elif self.filename[-3:len(self.filename)] == 'srt' and self.text[0][0] == '1' and self.text[1].find('-->') != -1:
            
            print(".srt file detected")
            line_counter = 0
            cc_text = ""
            cc_type = 1
            cc_time = 0
            start_time = 0
            end_time = 0

            for line in self.text:

                if len(line) > 0:

                    if line.find('-->') != -1 and line[0].isnumeric(): # timecode
                        start = line.split("-->")[0]
                        end = line.split("-->")[1]
                        hrs_start = int(start.split(":")[0])
                        min_start = int(start.split(":")[1])
                        sec_start = int(start.split(":")[2].split(',')[0])
                        ms_start = int(start.split(":")[2].split(',')[1])

                        hrs_end = int(end.split(":")[0])
                        min_end = int(end.split(":")[1])
                        sec_end = int(end.split(":")[2].split(',')[0])
                        ms_end = int(end.split(":")[2].split(',')[1])

                        start_time = Time(hrs_start, min_start, sec_start, ms_start)
                        end_time = Time(hrs_end, min_end, sec_end, ms_end)

                    elif line[0:2].find('>>') != -1: # person
                        cc_type = 1
                        cc_name = line[2:len(line)].split(":")[0]
                        text_tmp = line[2:len(line)].split(":")[1]
                        cc_text = text_tmp[1:len(text_tmp)]
                        
                        newPerson = True
                        for person in self.people:
                            if person == cc_name:
                                newPerson = False
                                break
                        
                        if newPerson:
                            self.people.append(cc_name)

                    elif line[0] == '[': # event
                        cc_type = 2
                        cc_name = ''
                        cc_text = line.split('[')[1].split(']')[0]
                    
                    elif(len(line) > 1): # plain text line
                        
                        if len(cc_text) == 0: # no previous line
                            cc_name = "noname"
                            cc_type = 0
                            cc_text = line

                            
                        else: # second line
                            cc_text += " " + line

                else: # len(line == 0) equivalent of '\n'
                    self.captions.append( Caption(cc_type, cc_name, cc_text, start_time, end_time) )
                    cc_text = ""

                line_counter += 1
                if line_counter == len(self.text): # on exit
                    if len(cc_text) > 0:
                        self.captions.append( Caption(cc_type, cc_name, cc_text, start_time, end_time) )

        elif self.filename[-3:len(self.filename)] == 'sbv' and self.text[0].find(',') != -1:
            
            print(".sbv file detected")
            self.file_type = 1
            line_counter = 0
            cc_text = ""
            cc_type = 1
            cc_time = 0
            start_time = 0
            end_time = 0

            for line in self.text:

                if len(line) > 0:

                    if (line[0].isnumeric() and line.find(':') != -1 # timecode
                        and line.find(',') != -1):

                        start = line.split(",")[0]
                        end = line.split(",")[1]
                        hrs_start = int(start.split(":")[0])
                        min_start = int(start.split(":")[1])
                        sec_start = int(start.split(":")[2].split('.')[0])
                        ms_start = int(start.split(":")[2].split('.')[1])

                        hrs_end = int(end.split(":")[0])
                        min_end = int(end.split(":")[1])
                        sec_end = int(end.split(":")[2].split('.')[0])
                        ms_end = int(end.split(":")[2].split('.')[1])

                        start_time = Time(hrs_start, min_start, sec_start, ms_start)
                        end_time = Time(hrs_end, min_end, sec_end, ms_end)

                    elif line[0:2].find('>>') != -1: # person
                        cc_type = 1
                        cc_name = line[2:len(line)].split(":")[0]
                        text_tmp = line[2:len(line)].split(":")[1]
                        cc_text = text_tmp[1:len(text_tmp)]
                        
                        newPerson = True
                        for person in self.people:
                            if person == cc_name:
                                newPerson = False
                                break
                        
                        if newPerson:
                            self.people.append(cc_name)

                    elif line[0] == '[': # event
                        cc_type = 2
                        cc_name = ''
                        cc_text = line.split('[')[1].split(']')[0]
                    
                    elif(len(line) > 1): # plain text line
                        
                        if len(cc_text) == 0: # no previous line
                            cc_name = "noname"
                            cc_type = 0
                            cc_text = line

                            
                        else: # second line
                            cc_text += " " + line

                else: # len(line == 0) equivalent of '\n'
                    self.captions.append( Caption(cc_type, cc_name, cc_text, start_time, end_time) )
                    cc_text = ""

                line_counter += 1
                if line_counter == len(self.text): # on exit
                    if len(cc_text) > 0:
                        self.captions.append( Caption(cc_type, cc_name, cc_text, start_time, end_time) )

            self.file_type = 2

        else:
            print("please try .txt, .srt or .sbv file")
        
        if (self.file_type != -1):
            print("ok")


class CustomPropertyGroup(bpy.types.PropertyGroup):
    string_field: bpy.props.StringProperty(name='text')

class ImportTranscript(Operator, ImportHelper):
    bl_idname = "_import.cc_file"
    bl_label = "Import Some Data"

    def execute(self, context):

        if DEBUG:
            test_file = r'C:\Users\marco\blender-gtts\tests\transcript_test.sbv'
            f = Path(bpy.path.abspath(test_file))
            ClosedCaptionSet(f.read_text().split("\n"), test_file)
            return {'FINISHED'}

        else:
            f = Path(bpy.path.abspath(self.filepath))
            if f.exists():
                ClosedCaptionSet(f.read_text().split("\n"), self.filepath)
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
                                            channel=2 )

        for strip in seq.sequences_all:
            print(strip.frame_duration)
            #print(strip.frame_start)
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
        bpy.ops._import.cc_file('INVOKE_DEFAULT')
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
          cc_type
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