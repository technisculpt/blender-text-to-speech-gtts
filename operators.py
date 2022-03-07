import os
import sys
import time
from datetime import timedelta
from pathlib import Path
import importlib

from threading import activeCount

import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper
from bpy.app.handlers import persistent

# append dir to path for dev, for prod use from . import module
dir = r'/home/magag/text_to_speech'
if os.name == 'nt':
    dir = r"C:\Users\marco\blender-text-to-speech"
sys.path.append(dir)

import text_to_sound as tts
importlib.reload(tts)

global global_captions
global_captions = []

if os.name == 'nt':
    output_dir = r'C:\\tmp\\'
else:
    output_dir = r'/tmp/'

@persistent
def load_handler(_scene):
    global global_captions

    if bpy.context.scene.text_to_speech.persistent_string:

        context = bpy.context
        scene = context.scene
        seq = scene.sequence_editor

        captions_raw = bpy.context.scene.text_to_speech.persistent_string.split('`')
        for caption in captions_raw:

            captions_split = caption.split('GTTS_TEXT')
            caption_meta = captions_split[0].split('|')

            if len(caption_meta) > 1:

                strip_name = caption_meta[0]
                cc_type = caption_meta[1]
                accent = caption_meta[2]
                name = caption_meta[3]
                channel = caption_meta[4]
                caption_strip = -1

                for strip in seq.sequences_all:
                    if strip.name == strip_name:
                        caption_strip = strip

                if caption_strip != -1:

                    # cc_type, name, text, start_time, end_time, accent, channel
                    new_cap = Caption(cc_type, name, -1,
                            Time(0, 0, 0, 0), Time(-1, -1, -1, -1),
                            accent, channel)
                    new_cap.sound_strip = caption_strip
                    new_cap.update_timecode()
    else:
        print("data not found")

def remove_deleted_strips():
    global global_captions

    for index, caption in enumerate(global_captions):
        if not caption.sound_strip.name:
            print(caption.sound_strip.name)
            del global_captions[index]

def sort_strips_by_time():
    global global_captions
    
    for caption in global_captions:
        caption.update_timecode()
    
    global_captions.sort(key=lambda caption: caption.current_seconds, reverse=False)

@persistent
def save_handler(_scene):
    global global_captions
    remove_deleted_strips()
    sort_strips_by_time()

    string_to_save = ""
    for caption in global_captions:

        string_to_save += f"{caption.sound_strip.name}|{caption.cc_type}|{caption.accent}|{caption.name}|{caption.channel}GTTS_TEXT{caption.text}`"

    bpy.context.scene.text_to_speech.persistent_string = string_to_save

def ensure_two_chars(number):
    string = str(number)

    if len(string) == 1:
        return '0' + string
    elif len(string) > 3:
        return string[0:3]
    else:
        return string

class Time():
    def __init__(self, hours=0, minutes=0, seconds=0, milliseconds=0):
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

    def frame_to_time(self, frames):
        td = timedelta(seconds=(frames / bpy.context.scene.render.fps))
        if (td.seconds/3600 >= 1):
            self.hours = int(td.seconds/3600)
        else:
            self.hours = 0
        if (td.seconds/60 >= 1):
            self.minutes = int(td.seconds/60)
        else:
            self.minutes = 0
        if (td.seconds >= 1):
            self.seconds = int(td.seconds)
        else:
            self.seconds = 0
        self.milliseconds = int(td.microseconds * 1000)
        return

class Caption():
    def __init__(self, cc_type, name, text, start_time, end_time, accent, channel):
        self.cc_type = cc_type # 0 : default, 1 : person, 2 : event
        self.accent = accent
        self.name = name
        self.text = text
        self.start_time = start_time
        self.end_time = end_time
        self.frame_start = start_time.time_to_frame()
        self.channel = channel

        if text != -1:
            if self.frame_start != -1:
                self.sound_strip = tts.sound_strip_from_text(text, self.frame_start, accent, channel)
            else:
                self.sound_strip = tts.sound_strip_from_text(text, 0, accent, channel)
        else:
            self.sound_strip = ""

    def update_timecode(self):
        self.start_time.frame_to_time(self.sound_strip.frame_start)
        self.end_time.frame_to_time(self.sound_strip.frame_final_end)
        self.current_seconds = self.sound_strip.frame_start / bpy.context.scene.render.fps

class ClosedCaptionSet(): # translates cc files into a list of Captions
    captions = []
    people = []

    def return_objects(self):
        return self.captions

    def arrange_captions_by_time(self): # when timecode not provided

        bpy.ops.sequencer.select_all(action='DESELECT')

        frame_pointer = 0
        for caption in range(len(self.captions)):

            if caption > 0:

                self.captions[caption].sound_strip.select = True
                bpy.ops.transform.seq_slide(value=(frame_pointer, 0))
                self.captions[caption].sound_strip.select = False
 
            frame_pointer += self.captions[caption].sound_strip.frame_duration + bpy.context.scene.render.fps

    def __init__(self, text, filename, accent):
        self.text = text
        self.filename = filename
        self.file_type = -1
        self.accent = accent

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
                    self.captions.append(Caption(cc_type, cc_name, cc_text, Time(-1, -1, -1, -1), Time(-1, -1, -1, -1), self.accent, 1))
                    cc_text = ""

                line_counter += 1
                if line_counter == len(self.text): # on exit
                    if len(cc_text) > 0:
                        self.captions.append(Caption(cc_type, cc_name, cc_text, Time(-1, -1, -1, -1), Time(-1, -1, -1, -1), self.accent, 1))

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
                    self.captions.append(Caption(cc_type, cc_name, cc_text, start_time, end_time, self.accent, 1))
                    cc_text = ""

                line_counter += 1
                if line_counter == len(self.text): # on exit
                    if len(cc_text) > 0:
                        self.captions.append(Caption(cc_type, cc_name, cc_text, start_time, end_time, self.accent, 1))

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
                    self.captions.append(Caption(cc_type, cc_name, cc_text, start_time, end_time, self.accent, 1))
                    cc_text = ""

                line_counter += 1
                if line_counter == len(self.text): # on exit
                    if len(cc_text) > 0:
                        self.captions.append(Caption(cc_type, cc_name, cc_text, start_time, end_time, self.accent, 1))

            self.file_type = 2

        else:
            print("please try .txt, .srt or .sbv file")

class TextToSpeechOperator(bpy.types.Operator):
    bl_idname = 'text_to_speech.speak'
    bl_label = 'speak op'
    bl_options = {'INTERNAL'}
    bl_description = "turns text into audio strip at current playhead"
  
    @classmethod
    def poll(cls, context):
        return context.object is not None
    
    def execute(self, context):
        global global_captions
        seconds = bpy.context.scene.frame_current / bpy.context.scene.render.fps
        
        if not context.scene.text_to_speech.string_field:
            print("no text to convert")
            self.report({'INFO'}, "FINISHED")
            return {'FINISHED'}
        else:
            global_captions.append(
                    Caption(0, context.scene.text_to_speech.string_field, context.scene.text_to_speech.string_field,
                    Time(0, 0, seconds, 0), Time(-1, -1, -1, -1),
                    context.scene.text_to_speech.accent_enumerator, 2))

            self.report({'INFO'}, "FINISHED")
            return {'FINISHED'}

class LoadFileOperator(bpy.types.Operator):
    bl_idname = 'text_to_speech.load'
    bl_label = 'load op'
    bl_options = {'INTERNAL'}
    bl_description = "loads closed captions from txt, srt or sbv file"

    @classmethod
    def poll(cls, context):
        return context.object is not None
    
    def execute(self, context):
        bpy.ops._import.cc_file('INVOKE_DEFAULT')
        self.report({'INFO'}, "done")
        return {'FINISHED'}

class ExportFileOperator(bpy.types.Operator):
    bl_idname = 'text_to_speech.export'
    bl_label = 'load op'
    bl_options = {'INTERNAL'}
    bl_description = "exports closed caption file to the render filepath"
  
    @classmethod
    def poll(cls, context):
        return context.object is not None
    
    def execute(self, context):
        global global_captions

        remove_deleted_strips()
        sort_strips_by_time()

        mode = context.scene.text_to_speech.mode_enumerator
        
        if mode == '0':

            print("exporting to .txt file")

            try:
                f = open(bpy.context.scene.render.filepath + "\captions_" +  time.strftime("%Y%m%d-%H%M%S") + ".txt", "x")
            except:
                f = open(bpy.context.scene.render.filepath + "\captions_" +  time.strftime("%Y%m%d-%H%M%S") + ".txt", "w")

            for caption in range(len(global_captions)):

                if global_captions[caption].cc_type == 0: # default text

                    f.write(global_captions[caption].text + '\n')

                elif global_captions[caption].cc_type == 1: # person

                    f.write(">> " + global_captions[caption].name + ': ' + global_captions[caption].text + '\n')

                elif global_captions[caption].cc_type == 2: # event

                    f.write('[' + global_captions[caption].text + ']\n' )

                if caption < len(global_captions):
                    f.write('\n')

            f.close()
            self.report({'INFO'}, "FINISHED")
            return {'FINISHED'}

        elif mode == '1': # srt file

            print("exporting to .srt file")
            
            try:
                f = open(bpy.context.scene.render.filepath + "\captions_" +  time.strftime("%Y%m%d-%H%M%S") + ".srt", "x")
            except:
                f = open(bpy.context.scene.render.filepath + "\captions_" +  time.strftime("%Y%m%d-%H%M%S") + ".srt", "w")

            for caption in range(len(global_captions)):

                f.write(str(caption + 1) + '\n')

                time_start = (ensure_two_chars(global_captions[caption].start_time.hours) + ':'
                            + ensure_two_chars(global_captions[caption].start_time.minutes) + ':'
                            + ensure_two_chars(global_captions[caption].start_time.seconds) + ','
                            + ensure_two_chars(global_captions[caption].start_time.milliseconds))

                time_end = (ensure_two_chars(global_captions[caption].end_time.hours) + ':'
                        + ensure_two_chars(global_captions[caption].end_time.minutes) + ':'
                        + ensure_two_chars(global_captions[caption].end_time.seconds) + ','
                        + ensure_two_chars(global_captions[caption].end_time.milliseconds))

                f.write(time_start + " --> " + time_end + '\n')

                if global_captions[caption].cc_type == 0: # default text

                    f.write(global_captions[caption].text + '\n')

                elif global_captions[caption].cc_type == 1: # person

                    f.write(">> " + global_captions[caption].name + ': ' + global_captions[caption].text + '\n')

                elif global_captions[caption].cc_type == 2: # event

                    f.write('[' + global_captions[caption].text + ']\n' )

                if caption < len(global_captions):
                    f.write('\n')
            
            f.close()
            self.report({'INFO'}, "FINISHED")
            return {'FINISHED'}

        else:

            print("exporting to .sbv file")

            try:
                f = open(bpy.context.scene.render.filepath + "\captions_" +  time.strftime("%Y%m%d-%H%M%S") + ".sbv", "x")
            except:
                f = open(bpy.context.scene.render.filepath + "\captions_" +  time.strftime("%Y%m%d-%H%M%S") + ".sbv", "w")

            for caption in range(len(global_captions)):

                time_start = (ensure_two_chars(str(global_captions[caption].start_time.hours)) + ':'
                            + ensure_two_chars(str(global_captions[caption].start_time.minutes)) + ':'
                            + ensure_two_chars(str(global_captions[caption].start_time.seconds)) + '.'
                            + ensure_two_chars(str(global_captions[caption].start_time.milliseconds)))

                time_end = (ensure_two_chars(str(global_captions[caption].end_time.hours)) + ':'
                        + ensure_two_chars(str(global_captions[caption].end_time.minutes)) + ':'
                        + ensure_two_chars(str(global_captions[caption].end_time.seconds)) + '.'
                        + ensure_two_chars(str(global_captions[caption].end_time.milliseconds)))

                f.write(time_start + "," + time_end + '\n')

                if global_captions[caption].cc_type == 0: # default text

                    f.write(global_captions[caption].text + '\n')

                elif global_captions[caption].cc_type == 1: # person

                    f.write(">> " + global_captions[caption].name + ': ' + global_captions[caption].text + '\n')

                elif global_captions[caption].cc_type == 2: # event

                    f.write('[' + global_captions[caption].text + ']\n' )

                if caption < len(global_captions):
                    f.write('\n')
            
            f.close()
            self.report({'INFO'}, "FINISHED")
            return {'FINISHED'}

class ImportTranscript(Operator, ImportHelper):
    bl_idname = "_import.cc_file"
    bl_label = "Import Some Data"

    def execute(self, context):
        global global_captions
        f = Path(bpy.path.abspath(self.filepath))
        if f.exists():
            ccs =  ClosedCaptionSet(f.read_text().split("\n"), self.filepath,
                context.scene.text_to_speech.accent_enumerator)
            global_captions += ccs.return_objects()
            return {'FINISHED'}
