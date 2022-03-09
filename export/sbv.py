# append dir to path for dev, for prod use from . import module
import sys
import os

dir = r'/home/magag/text_to_speech/export'
if os.name == 'nt':
    dir = r"C:\Users\marco\blender-text-to-speech\export"
sys.path.append(dir)

import bpy

import importlib
import export_helper as lib
importlib.reload(lib)

def export(filepath, captions):
    try:
        with open(f"{filepath}.sbv", "x") as f:

            for caption in range(len(captions)):

                time_start = (lib.ensure_two_chars(captions[caption].start_time.hours) + ':'
                            + lib.ensure_two_chars(captions[caption].start_time.minutes) + ':'
                            + lib.ensure_two_chars(captions[caption].start_time.seconds) + '.'
                            + lib.ensure_two_chars(captions[caption].start_time.milliseconds))

                time_end = (lib.ensure_two_chars(captions[caption].end_time.hours) + ':'
                        + lib.ensure_two_chars(captions[caption].end_time.minutes) + ':'
                        + lib.ensure_two_chars(captions[caption].end_time.seconds) + '.'
                        + lib.ensure_two_chars(captions[caption].end_time.milliseconds))

                f.write(f"{time_start}, {time_end}\n")

                if captions[caption].cc_type == 0: # default text

                    f.write(f"{captions[caption].text}\n")

                elif captions[caption].cc_type == 1: # person

                    f.write(f">>{captions[caption].name}: {captions[caption].text}\n")

                elif captions[caption].cc_type == 2: # event

                    f.write(f"[{captions[caption].text}]\n")

                if caption < len(captions):
                    f.write('\n')

        return(True)

    except FileExistsError:
        print("File already exists")
        return(False)