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

DEBUG = True

if os.name == 'nt':
    output_dir = r'C:\\tmp\\'
else:
    output_dir = r'/tmp/'

def sound_strip_from_text(tts, start_frame, language="en", top_level_domain="com.au"):

    if os.name == 'nt':
        output_name = output_dir + '\\' + tts + ".mp3"
    else:
        output_name = output_dir +  '/' + tts + ".mp3"

    ttmp3 = gTTS(text=tts, lang=language, tld=top_level_domain)
    ttmp3.save(output_name)
    scene = context.scene
    
    if not scene.sequence_editor:
        scene.sequence_editor_create()
    seq = scene.sequence_editor

    bpy.ops.sequencer.sound_strip_add(  filepath=output_name,
                                        frame_start=start_frame,
                                        channel=2, )

    obj = ''
    for strip in seq.sequences_all:
        if output_name.find(strip.name) != -1:
            obj = strip
            break

    #obj.pitch = 0.85

    return obj

class Time():

    def __init__(self, hours, minutes, seconds, milliseconds):
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
        self.milliseconds = milliseconds

    def time_to_frame(self):
        if self.hours == -1:
            return self.hours
        else:
            total_seconds = self.hours * 3600 + self.minutes * 60 + self.seconds + self.milliseconds/1000
        return total_seconds * bpy.context.scene.render.fps

class Caption():

    def __init__(self, cc_type, name, text, start_time, end_time):
        self.rearrange = False
        self.cc_type = cc_type # 0 : default, 1 : person, 2 : event
        self.name = name
        self.text = text
        self.start_time = start_time
        self.end_time = end_time
        self.frame_start = start_time.time_to_frame()
        if self.frame_start != -1:
            self.sound_strip = sound_strip_from_text(text, self.frame_start)
        else:
            self.sound_strip = sound_strip_from_text(text, 0)

class ClosedCaptionSet():

    captions = []
    people = []

    def arrange_captions_by_time(self):
        
        frame_pointer = 0
        for caption in range(len(self.captions)):

            if caption > 0:

                self.captions[caption].sound_strip.frame_start = frame_pointer

            frame_pointer += self.captions[caption].sound_strip.frame_duration

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

            self.arrange_captions_by_time()
            
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
            test_file = r'C:\Users\marco\blender-gtts\tests\transcript_test.txt'
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
        layout.operator('custom.speak', text = 'add caption')
        layout.prop(context.scene.custom_props, 'string_field')
        layout.operator('custom.load', text = 'load captions file')

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

        
        sound_strip_from_text(context.scene.custom_props.string_field, bpy.context.scene.frame_current)

 

        self.report({'INFO'}, "FINISHED")
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

Local accent

Language code (lang)

Top-level domain (tld)

English (Australia)

en

com.au

English (United Kingdom)

en

co.uk

English (United States)

en

com (default)

English (Canada)

en

ca

English (India)

en

co.in

English (Ireland)

en

ie

English (South Africa)

en

co.za

French (Canada)

fr

ca

French (France)

fr

fr

Mandarin (China Mainland)

zh-CN

any

Mandarin (Taiwan)

zh-TW

any

Portuguese (Brazil)

pt

com.br

Portuguese (Portugal)

pt

pt

Spanish (Mexico)

es

com.mx

Spanish (Spain)

es

es

Spanish (United States)

es

com (default)


'''