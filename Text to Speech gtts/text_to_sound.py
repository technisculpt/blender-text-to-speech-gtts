from gtts import gTTS
import os
import time
import bpy
from sys import platform

not_allowed = ['/']
if platform == "win32":
    not_allowed = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']

accents_domain = ["com.au","co.uk","com","ca","co.in","ie","co.za","ca","fr","com","com","com.br","pt","com.mx","es","com"]

languages = ['af', 'ar', 'bg', 'bn', 'bs', 'ca', 'cs', 'cy', 'da', 'de', 'el', 'en', 'eo', 'es', 'et',
            'fi', 'fr', 'gu', 'hi', 'hr', 'hu', 'hy', 'id', 'is', 'it', 'iw', 'ja', 'jw', 'km', 'kn',
            'ko', 'la', 'lv', 'mk', 'ms', 'ml', 'mr', 'my', 'ne', 'nl', 'no', 'pl', 'pt', 'ro', 'ru',
            'si', 'sk', 'sq', 'sr', 'su', 'sv', 'sw', 'ta', 'te', 'th', 'tl', 'tr', 'uk', 'ur', 'vi',
            'zh-CN', 'zh-TW', 'zh']

def sound_strip_from_text(context, tts, pitch, start_frame, accent_enum, audio_channel, language):

    top_level_domain = accents_domain[int(accent_enum)]
    language = languages[int(language)]

    tmp_ident = tts[0:45]
    
    text_ident = ""
    for char in tmp_ident:
        if char in not_allowed:
            pass
        else:
            text_ident += char

    relpath = False
    filepath_full = bpy.context.scene.render.filepath
    if (bpy.context.scene.render.filepath[0:2] == "//"):
        relpath = True
        filepath_full = bpy.path.abspath(bpy.context.scene.render.filepath)


    identifier = f'{text_ident}{time.strftime("%Y%m%d%H%M%S")}'
    output_name = os.path.join(filepath_full, identifier + ".mp3")

    ttmp3 = gTTS(text=tts, lang=language, tld=top_level_domain)
    ttmp3.save(output_name)

    _scene = context.scene
    
    if not _scene.sequence_editor:
        _scene.sequence_editor_create()
    seq = _scene.sequence_editor

    if relpath:
        obj = seq.sequences.new_sound(identifier, filepath=bpy.path.relpath(output_name), channel=audio_channel, frame_start=start_frame)
    else:
        obj = seq.sequences.new_sound(identifier, filepath=output_name, channel=audio_channel, frame_start=start_frame)

    
    obj.pitch = pitch
    
    return (obj, identifier)