from gtts import gTTS
import os
from pathlib import Path
from datetime import date, datetime, timedelta

import bpy
from bpy import context
from bpy_extras.io_utils import ImportHelper
from bpy.types import Operator

global global_captions
global_captions = []

accents_domain = ["com.au","co.uk","com","ca","co.in","ie","co.za","ca","fr","com.br","pt","com.mx","es","com"]
accents_lang = ["en","en","en","en","en","en","en","fr","fr","pt","pt","es","es","es"]

if os.name == 'nt':
    output_dir = r'C:\\tmp\\'
else:
    output_dir = r'/tmp/'

def refresh_strip_times():
    global global_captions
    
    for caption in global_captions:
        caption.update_timecode()
    
    global_captions.sort(key=lambda caption: caption.current_seconds, reverse=False)

def ensure_two_chars(number):
    
    string = str(number)

    if len(string) == 1:
        return '0' + string
    elif len(string) > 3:
        return string[0:3]
    else:
        return string

def sound_strip_from_text(tts, start_frame, accent_enum, pitch_shift):
    actual_text = tts
    tts = tts[0:4]
    dupe_found = False
    top_level_domain = accents_domain[int(accent_enum)]
    language = accents_lang[int(accent_enum)]

    if os.name == 'nt':
        output_name = output_dir + '\\' + tts + ".mp3"
    else:
        output_name = output_dir +  '/' + tts + ".mp3"

    filename = Path(output_name)

    if not filename.exists():
        ttmp3 = gTTS(text=actual_text, lang=language, tld=top_level_domain)
        ttmp3.save(output_name)

    else:

        find_unique_name = True
        tts_copy = tts
        c = 0
        dupe_found = True
        while(find_unique_name):
            if os.name == 'nt':
                output_name = output_dir + '\\' + tts_copy + str(c) + ".mp3"
            else:
                output_name = output_dir +  '/' + tts_copy + str(c) + ".mp3"
            filename = Path(output_name)
            if not filename.exists():
                ttmp3 = gTTS(text=actual_text, lang=language, tld=top_level_domain)
                ttmp3.save(output_name)
                find_unique_name = False
            else:
                c += 1

    scene = context.scene
    
    if not scene.sequence_editor:
        scene.sequence_editor_create()
    seq = scene.sequence_editor


    obj = bpy.ops.sequencer.sound_strip_add(filepath=output_name,
                                        frame_start=start_frame,
                                        )

    obj = -1
    found = []
    
    if dupe_found:
        label = tts_copy + str(c)
    else:
        label = tts

    for strip in seq.sequences_all:
        if strip.name.find(label) != -1:
            obj = strip
            found.append(strip)

    if len(found) > 1:
        print("huh")

    if obj != -1:
        obj.pitch = pitch_shift
        return obj

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

    def __init__(self, cc_type, name, text, start_time, end_time, accent, pitch):
        self.rearrange = False
        self.cc_type = cc_type # 0 : default, 1 : person, 2 : event
        self.accent = accent
        self.name = name
        self.text = text
        self.start_time = start_time
        self.end_time = end_time
        self.frame_start = start_time.time_to_frame()
        self.pitch = pitch
        if self.frame_start != -1:
            self.sound_strip = sound_strip_from_text(text, self.frame_start, self.accent, self.pitch)
        else:
            self.sound_strip = sound_strip_from_text(text, 0, self.accent, self.pitch)

    def update_timecode(self):
        self.start_time.frame_to_time(self.sound_strip.frame_start)
        self.end_time.frame_to_time(self.sound_strip.frame_final_end) #bpy.context.scene.render.fps
        self.current_seconds = self.sound_strip.frame_start / bpy.context.scene.render.fps

class ClosedCaptionSet(): # translates cc files into a list of Captions

    captions = []
    people = []

    def return_objects(self):
        return self.captions

    def arrange_captions_by_time(self): # when timecode not provided
        
        frame_pointer = 0
        for caption in range(len(self.captions)):

            if caption > 0:

                self.captions[caption].sound_strip.frame_start = frame_pointer

            frame_pointer += self.captions[caption].sound_strip.frame_duration

    def __init__(self, text, filename, accent, pitch):
        self.text = text
        self.filename = filename
        self.file_type = -1
        self.accent = accent
        self.pitch = pitch

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
                    self.captions.append( Caption(cc_type, cc_name, cc_text, Time(-1, -1, -1, -1), Time(-1, -1, -1, -1), self.accent, self.pitch) )
                    cc_text = ""

                line_counter += 1
                if line_counter == len(self.text): # on exit
                    if len(cc_text) > 0:
                        self.captions.append( Caption(cc_type, cc_name, cc_text, Time(-1, -1, -1, -1), Time(-1, -1, -1, -1), self.accent, self.pitch) )

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
                    self.captions.append( Caption(cc_type, cc_name, cc_text, start_time, end_time, self.accent, self.pitch) )
                    cc_text = ""

                line_counter += 1
                if line_counter == len(self.text): # on exit
                    if len(cc_text) > 0:
                        self.captions.append( Caption(cc_type, cc_name, cc_text, start_time, end_time, self.accent, self.pitch) )

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
                    self.captions.append( Caption(cc_type, cc_name, cc_text, start_time, end_time, self.accent, self.pitch) )
                    cc_text = ""

                line_counter += 1
                if line_counter == len(self.text): # on exit
                    if len(cc_text) > 0:
                        self.captions.append( Caption(cc_type, cc_name, cc_text, start_time, end_time, self.accent, self.pitch) )

            self.file_type = 2

        else:
            print("please try .txt, .srt or .sbv file")

class TextToSpeechOperator(bpy.types.Operator):
    bl_idname = 'custom.speak'
    bl_label = 'speak op'
    bl_options = {'INTERNAL'}
    bl_description = "turns text into audio strip at current playhead"
  
    @classmethod
    def poll(cls, context):
        return context.object is not None
    
    def execute(self, context):
        global global_captions
        seconds = bpy.context.scene.frame_current / bpy.context.scene.render.fps
        
        if not context.scene.custom_props.string_field:
            print("no text to convert")
            self.report({'INFO'}, "FINISHED")
            return {'FINISHED'}
        else:
            global_captions.append(Caption(0, '', context.scene.custom_props.string_field, Time(0, 0, seconds, 0), Time(-1, -1, -1, -1), context.scene.custom_props.accent_enumerator, context.scene.custom_props.pitch))
            self.report({'INFO'}, "FINISHED")
            return {'FINISHED'}

class LoadFileOperator(bpy.types.Operator):
    bl_idname = 'custom.load'
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
    bl_idname = 'custom.export'
    bl_label = 'load op'
    bl_options = {'INTERNAL'}
    bl_description = "exports closed caption file to the render filepath"
  
    @classmethod
    def poll(cls, context):
        return context.object is not None
    
    def execute(self, context):

        global global_captions

        refresh_strip_times()

        mode = context.scene.export_options.mode_enumerator
        
        if mode == '0':

            print("exporting to .txt file")

            try:
                f = open(bpy.context.scene.render.filepath + "\captions_" +  datetime.today().strftime('%Y-%m-%d') + ".txt", "x")
            except:
                f = open(bpy.context.scene.render.filepath + "\captions_" +  datetime.today().strftime('%Y-%m-%d') + ".txt", "w")

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
                f = open(bpy.context.scene.render.filepath + "\captions_" +  datetime.today().strftime('%Y-%m-%d') + ".srt", "x")
            except:
                f = open(bpy.context.scene.render.filepath + "\captions_" +  datetime.today().strftime('%Y-%m-%d') + ".srt", "w")

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
                f = open(bpy.context.scene.render.filepath + "\captions_" +  datetime.today().strftime('%Y-%m-%d') + ".sbv", "x")
            except:
                f = open(bpy.context.scene.render.filepath + "\captions_" +  datetime.today().strftime('%Y-%m-%d') + ".sbv", "w")

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
            ccs =  ClosedCaptionSet(f.read_text().split("\n"), self.filepath, context.scene.custom_props.accent_enumerator, context.scene.custom_props.pitch)
            global_captions += ccs.return_objects()
            return {'FINISHED'}
