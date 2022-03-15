import bpy

class TextToSpeechSettings(bpy.types.PropertyGroup):
    persistent_string : bpy.props.StringProperty(name='Persistent String')
    string_field : bpy.props.StringProperty(name='Text')
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
                        ('12',"Spain (US)","")]
        )
    pitch : bpy.props.FloatProperty(
        name="Pitch",
        description="Speechify pitch",
        default=1.0,
        min=0.1, max=10.0,
        )
        

class TextToSpeech_PT(bpy.types.Panel):
    bl_space_type = 'SEQUENCE_EDITOR'
    bl_region_type = 'UI'
    bl_label = 'Text To Speech'
    bl_category = 'Text To Speech'
    bl_idname = 'SEQUENCER_PT_text_to_speech'

    def draw(self, context):
        layout = self.layout

        col = layout.column(align=True)
        col.use_property_split = True
        col.prop(context.scene.text_to_speech, 'accent_enumerator', text='Accent')
        
        col = layout.column(align=True)
        col.use_property_split = True
        col.prop(context.scene.text_to_speech, 'pitch', text='Pitch')

        box = layout.box()
        col = box.column(align=True)
        col.use_property_split = False
        col.prop(context.scene.text_to_speech, 'string_field', text = '')
        col.operator('text_to_speech.speak', text = 'Speechify', icon='ADD')

        col = layout.column()
        layout.operator('text_to_speech.load', text = 'Load Captions File',  icon='IMPORT')

        col = layout.column()
        subrow = layout.row(align=True)
        subrow.operator('text_to_speech.export', text = 'Export Captions File', icon='EXPORT')


