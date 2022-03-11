import os
import sys
from pathlib import Path
import importlib

import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.app.handlers import persistent
from bpy.props import StringProperty, EnumProperty, BoolProperty

from . import text_to_sound as tts
from . import blender_time as b_time
from . import caption as c
from .imports import txt as txt_import
from .imports import srt as srt_import
from .imports import sbv as sbv_import
from .exports import txt as txt_export
from .exports import srt as srt_export
from .exports import sbv as sbv_export

global global_captions
global_captions = []

def remove_deleted_strips():
    global global_captions

    sound_strips = []
    context = bpy.context
    scene = context.scene
    seq = scene.sequence_editor
    for strip in seq.sequences_all:
        sound_strips.append(strip.name)
        
    for index, caption in enumerate(global_captions):
        if caption.sound_strip.name not in sound_strips:
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
            cc_type = int(caption_meta[1])
            accent = caption_meta[2]
            name = caption_meta[3]
            channel = int(caption_meta[4])
            strip_text = caption_meta[5]
            caption_strip = -1

            for strip in seq.sequences_all:
                if strip.name == strip_name:
                    caption_strip = strip

            if caption_strip != -1:
                new_cap = c.Caption(context, cc_type, name, strip_text,
                        b_time.Time(-1, -1, -1, -1), b_time.Time(-1, -1, -1, -1),
                        accent, channel, reconstruct=True)
                new_cap.sound_strip = caption_strip
                new_cap.update_timecode()
                global_captions.append(new_cap)

@persistent
def save_handler(_scene):
    global global_captions
    remove_deleted_strips()
    sort_strips_by_time()
    string_to_save = ""
    
    for caption in global_captions:
        string_to_save += f"{caption.sound_strip.name}|{caption.cc_type}|{caption.accent}|{caption.name}|{caption.channel}|{caption.text}`"

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
            self.report({'INFO'}, "no text to convert")
            return {'FINISHED'}

        else:
            global_captions.append(
                    c.Caption(context, 0, "", context.scene.text_to_speech.string_field,
                    b_time.Time(0, 0, seconds, 0), b_time.Time(-1, -1, -1, -1),
                    context.scene.text_to_speech.accent_enumerator, 2))
            self.report({'INFO'}, "FINISHED")
            return {'FINISHED'}

class ClosedCaptionSet(): # translates cc files into a list of c.Captions
    captions = []
    people = []

    def get(self):
        return(self.captions)

    def arrange_captions_by_time(self): # when timecode not provided
        bpy.ops.sequencer.select_all(action='DESELECT')
        frame_pointer = 0

        for caption in range(len(self.captions)):

            if caption > 0:
                self.captions[caption].sound_strip.select = True
                bpy.ops.transform.seq_slide(value=(frame_pointer, 0))
                self.captions[caption].sound_strip.select = False
 
            frame_pointer += self.captions[caption].sound_strip.frame_duration + bpy.context.scene.render.fps

    def __init__(self, context, text, filename, accent):
        ext = filename[-3:len(filename)]
        self.finished = False

        if ext == 'txt':
            self.captions = txt_import.import_cc(context, text, accent)
            self.arrange_captions_by_time()
            self.finished = True
            
        elif ext == 'srt':
            self.captions = srt_import.import_cc(context, text, accent)
            self.finished = True

        elif ext == 'sbv':
            self.captions = sbv_import.import_cc(context, text, accent)
            self.finished = True

class ImportClosedCapFile(Operator, ImportHelper):
    bl_idname = "_import.cc_file"
    bl_label = "Import CC Data"

    def execute(self, context):
        global global_captions
        f = Path(bpy.path.abspath(self.filepath))

        if f.exists():
            captions =  ClosedCaptionSet(context, f.read_text().split("\n"), self.filepath,
                context.scene.text_to_speech.accent_enumerator)

            if captions.finished:
                global_captions += captions.get()
                return {'FINISHED'}

            else:
                self.report({'INFO'}, 'Please try .txt, .srt or .sbv file')
                return {'CANCELLED'}

class LoadFileButton(Operator):
    bl_idname = 'text_to_speech.load'
    bl_label = 'load op'
    bl_options = {'INTERNAL'}
    bl_description = "loads closed captions from txt, srt or sbv file"

    @classmethod
    def poll(cls, context):
        return context.object is not None
    
    def execute(self, context):
        bpy.ops._import.cc_file('INVOKE_DEFAULT')
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