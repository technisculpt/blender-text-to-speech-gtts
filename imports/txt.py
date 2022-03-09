# append dir to path for dev, for prod use from . import module
import sys
import os

dir = r'/home/magag/text_to_speech'
if os.name == 'nt':
    dir = r"C:\Users\marco\blender-text-to-speech"
sys.path.append(dir)

import bpy

import importlib
import blender_time as b_time
importlib.reload(b_time)
import blender_time as b_time
importlib.reload(b_time)
import caption as c
importlib.reload(c)

def import_cc(text, accent):
    print(".txt file detected")
    captions = []
    line_counter = 0
    cc_text = ""
    cc_type = 1

    for line in text:
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
            captions.append(c.Caption(cc_type, cc_name, cc_text, b_time.Time(-1, -1, -1, -1), b_time.Time(-1, -1, -1, -1), accent, 1))
            cc_text = ""

        line_counter += 1
        if line_counter == len(text): # on exit
            if len(cc_text) > 0:
                captions.append(c.Caption(cc_type, cc_name, cc_text, b_time.Time(-1, -1, -1, -1), b_time.Time(-1, -1, -1, -1), accent, 1))

    return(captions)