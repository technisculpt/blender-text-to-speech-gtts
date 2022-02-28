import bpy

class TextToSpeechSettings(bpy.types.PropertyGroup):

    string_field : bpy.props.StringProperty(name='text')

    '''
    pitch : bpy.props.FloatProperty(
        name="Pitch",
        description="Control pitch",
        default=1.0,
        min=0.1,
        max=10.0)
    '''
    
    accent_enumerator : bpy.props.EnumProperty(
                name = "",
                description = "accent options for speakers",
                items=[ ('0',"Australia",""),
                        ('1',"United Kingdom",""),
                        ('2',"Canada",""),
                        ('3',"India",""),
                        ('4',"Ireland",""),
                        ('5',"South Africa",""),
                        ('6',"French Canada",""),
                        ('7',"France",""),
                        ('8',"Brazil",""),
                        ('9',"Portugal",""),
                        ('10',"Mexico",""),
                        ('11',"Spain",""),
                        ('12',"Spain (US)","")])

    mode_enumerator : bpy.props.EnumProperty(
                    name = "",
                    description = "export options for closed captions",
                    items=[('0',"txt",""),('1',"srt",""),('2',"sbv","")])

class TextToSpeech_PT(bpy.types.Panel):
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_label = 'textToSpeech'
    bl_category = 'Text To Speech'
    bl_idname = 'SEQUENCER_PT_textToSpeech'

    def draw(self, context):
        layout = self.layout
        col = layout.column()
        col.label(text="Add Caption:")
        layout.prop(context.scene.text_to_speech, 'string_field')
        layout.operator('text_to_speech.speak', text = 'add caption')
        col = layout.column()
        col.label(text="Load Captions:")
        layout.operator('text_to_speech.load', text = 'load captions file')

        col = layout.column()
        col.label(text="Export Captions:")
        subrow = layout.row(align=True)
        subrow.prop(context.scene.text_to_speech, 'mode_enumerator')
        subrow.operator('text_to_speech.export', text = 'export')

        col = layout.column()
        col.label(text="Accent:")
        subrow = layout.row(align=True)
        subrow.prop(context.scene.text_to_speech, 'accent_enumerator')
        #subrow.prop(context.scene.text_to_speech, 'pitch')