import os
import sys
from pathlib import Path
import importlib

import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.app.handlers import persistent
from bpy.props import StringProperty, EnumProperty, BoolProperty

# append dir to path for dev, for prod use from . import module
dir = r'/home/magag/text_to_speech'
if os.name == 'nt':
    dir = r"C:\Users\marco\blender-text-to-speech"
sys.path.append(dir)

import text_to_sound as tts
importlib.reload(tts)
import export.txt as txt_export
importlib.reload(txt_export)
import export.srt as srt_export
importlib.reload(srt_export)
import export.sbv as sbv_export
importlib.reload(sbv_export)
import blender_time as b_time
importlib.reload(b_time)
import caption as c
importlib.reload(c)

global global_captions
global_captions = []

def remove_deleted_strips():
    global global_captions
    
    for index, caption in enumerate(global_captions):
        if not caption.sound_strip.name:
            del global_captions[index]

def sort_strips_by_time():
    global global_captions
    
    for caption in global_captions:
        caption.update_timecode()
    
    global_captions.sort(key=lambda caption: caption.current_seconds, reverse=False)

@persistent
def load_handler(_scene):
    global global_captions

    if bpy.context.scene.text_to_speech.persistent_string:

        context = bpy.context
        scene = context.scene
        seq = scene.sequence_editor
        captions_raw = bpy.context.scene.text_to_speech.persistent_string.split('`')
        captions_raw.pop()

        for caption in captions_raw:

            caption_meta = caption.split('|')
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
                # cc_type, name, text, start_time, time_end, accent, channel
                new_cap = c.Caption(cc_type, name, -1,
                        b_time.Time(0, 0, 0, 0), b_time.Time(-1, -1, -1, -1),
                        accent, channel)
                new_cap.sound_strip = caption_strip
                new_cap.update_timecode()
    else:
        print("caption data not found")


@persistent
def save_handler(_scene):
    global global_captions
    remove_deleted_strips()
    sort_strips_by_time()

    string_to_save = ""
    for caption in global_captions:

        string_to_save += f"{caption.sound_strip.name}|{caption.cc_type}|{caption.accent}|{caption.name}|{caption.channel}`"

    bpy.context.scene.text_to_speech.persistent_string = string_to_save

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
                    c.Caption(0, "", context.scene.text_to_speech.string_field,
                    b_time.Time(0, 0, seconds, 0), b_time.Time(-1, -1, -1, -1),
                    context.scene.text_to_speech.accent_enumerator, 2))

            self.report({'INFO'}, "FINISHED")
            return {'FINISHED'}

class ClosedCaptionSet(): # translates cc files into a list of c.Captions
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
                    self.captions.append(c.Caption(cc_type, cc_name, cc_text, b_time.Time(-1, -1, -1, -1), b_time.Time(-1, -1, -1, -1), self.accent, 1))
                    cc_text = ""

                line_counter += 1
                if line_counter == len(self.text): # on exit
                    if len(cc_text) > 0:
                        self.captions.append(c.Caption(cc_type, cc_name, cc_text, b_time.Time(-1, -1, -1, -1), b_time.Time(-1, -1, -1, -1), self.accent, 1))

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

                        start_time = b_time.Time(hrs_start, min_start, sec_start, ms_start)
                        end_time = b_time.Time(hrs_end, min_end, sec_end, ms_end)

                    elif line[0:2].find('>>') != -1: # person
                        cc_type = 1
                        cc_name = line[2:len(line)].split(":")[0]
                        text_tmp = line[2:len(line)].split(":")[1]
                        cc_text = text_tmp[1:len(text_tmp)]

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
                    self.captions.append(c.Caption(cc_type, cc_name, cc_text, start_time, end_time, self.accent, 1))
                    cc_text = ""

                line_counter += 1
                if line_counter == len(self.text): # on exit
                    if len(cc_text) > 0:
                        self.captions.append(c.Caption(cc_type, cc_name, cc_text, start_time, end_time, self.accent, 1))

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

                        start_time = b_time.Time(hrs_start, min_start, sec_start, ms_start)
                        end_time = b_time.Time(hrs_end, min_end, sec_end, ms_end)

                    elif line[0:2].find('>>') != -1: # person
                        cc_type = 1
                        cc_name = line[2:len(line)].split(":")[0]
                        text_tmp = line[2:len(line)].split(":")[1]
                        cc_text = text_tmp[1:len(text_tmp)]

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
                    self.captions.append(c.Caption(cc_type, cc_name, cc_text, start_time, end_time, self.accent, 1))
                    cc_text = ""

                line_counter += 1
                if line_counter == len(self.text): # on exit
                    if len(cc_text) > 0:
                        self.captions.append(c.Caption(cc_type, cc_name, cc_text, start_time, end_time, self.accent, 1))

            self.file_type = 2

        else:
            print("please try .txt, .srt or .sbv file")


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

class ImportTranscript(Operator, ImportHelper):
    bl_idname = "_import.cc_file"
    bl_label = "Import CC Data"

    def execute(self, context):
        global global_captions
        f = Path(bpy.path.abspath(self.filepath))
        if f.exists():
            ccs =  ClosedCaptionSet(f.read_text().split("\n"), self.filepath,
                context.scene.text_to_speech.accent_enumerator)
            global_captions += ccs.return_objects()
            return {'FINISHED'}


def export_cc_file(context, filepath, file_type):
    global global_captions
    remove_deleted_strips()
    sort_strips_by_time()

    if file_type == 'txt':
        return(txt_export.export(filepath, global_captions))

    if file_type == 'srt':
        return(srt_export.export(filepath, global_captions))

    if file_type == 'sbv':
        return(sbv_export.export(filepath, global_captions))


class ExportFileName(Operator, ExportHelper):
    bl_idname = "_export.cc_file"
    bl_label = "Export CC Data"

    filename_ext = ""
    
    type: EnumProperty(
        name="Filetype",
        description="Choose File Type",
        items=(
            ("txt", "txt", "text file"),
            ("srt", "srt", "srt file"),
            ("sbv", "sbv", "sbv file"),
        ),
        default="txt",
    )

    def execute(self, context):
        if export_cc_file(context, self.filepath, self.type):
            return {'FINISHED'}
        else:
            self.report({'INFO'}, 'File already exists.')
            return {'CANCELLED'}

class ExportFileButton(Operator):
    bl_idname = 'text_to_speech.export'
    bl_label = 'export op'
    bl_options = {'INTERNAL'}
    bl_description = "exports closed caption file to a filepath"
  
    @classmethod
    def poll(cls, context):
        return {'FINISHED'}
    
    def execute(self, context):
        bpy.ops._export.cc_file('INVOKE_DEFAULT')
        return {'FINISHED'} 