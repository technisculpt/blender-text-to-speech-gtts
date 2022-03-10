from gtts import gTTS
import os
import time

import bpy
#from bpy import context

accents_domain = ["com.au","co.uk","com","ca","co.in","ie","co.za","ca","fr","com.br","pt","com.mx","es","com"]
accents_lang = ["en","en","en","en","en","en","en","fr","fr","pt","pt","es","es","es"]

def sound_strip_from_text(context, tts, start_frame, accent_enum, audio_channel):

    top_level_domain = accents_domain[int(accent_enum)]
    language = accents_lang[int(accent_enum)]

    output_name = os.path.join(bpy.context.scene.render.filepath, f'{tts}_{time.strftime("%Y%m%d-%H%M%S")}.mp3')

    ttmp3 = gTTS(text=tts, lang=language, tld=top_level_domain)
    ttmp3.save(output_name)

    _scene = context.scene
    
    if not _scene.sequence_editor:
        _scene.sequence_editor_create()
    seq = _scene.sequence_editor

    #obj = bpy.ops.sequencer.sound_strip_add(filepath=output_name, frame_start=start_frame)
    obj = seq.sequences.new_sound(tts, filepath=output_name, channel=audio_channel, frame_start=start_frame)
    
    return obj