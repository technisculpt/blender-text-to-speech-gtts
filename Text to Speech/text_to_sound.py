from gtts import gTTS
import os
import time

import bpy

accents_domain = ["com.au","co.uk","com","ca","co.in","ie","co.za","ca","fr","com","com","com.br","pt","com.mx","es","com"]
accents_lang = ["en","en","en","en","en","en","en","fr","fr","zh-CN","zh-TW","pt","pt","es","es","es"]

def sound_strip_from_text(context, tts, pitch, start_frame, accent_enum, audio_channel):

    top_level_domain = accents_domain[int(accent_enum)]
    language = accents_lang[int(accent_enum)]

    identifier = f'{tts[0:45]}{time.strftime("%Y%m%d%H%M%S")}'
    output_name = os.path.join(bpy.context.scene.render.filepath, identifier)

    ttmp3 = gTTS(text=tts, lang=language, tld=top_level_domain)
    ttmp3.save(output_name)

    _scene = context.scene
    
    if not _scene.sequence_editor:
        _scene.sequence_editor_create()
    seq = _scene.sequence_editor

    obj = seq.sequences.new_sound(identifier, filepath=output_name, channel=audio_channel, frame_start=start_frame)
    obj.pitch = pitch
    
    return (obj, identifier)