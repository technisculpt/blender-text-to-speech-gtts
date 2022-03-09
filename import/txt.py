# append dir to path for dev, for prod use from . import module
import sys
import os

dir = r'/home/magag/text_to_speech'
if os.name == 'nt':
    dir = r"C:\Users\marco\blender-text-to-speech"
sys.path.append(dir)

import bpy

import importlib
import time as b_time
importlib.reload(b_time)