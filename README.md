# blender-text-to-speech
### this is for educational use only! For commercial purposes see the other text to speech repo
* blender wrapper for gtts (google text to speech)
* make audio captions quickly
* options for input language, accent and pitch
* convert closed captions files to audio (.srt, .srb and .txt) audio strips placed at timecodes if provided
* importing .txt files with no timecodes will place the audio strips in sequence based on order and text length
* optional import/export to csv file to save pitch and language options of individual strips
* export the audio clips generated by the tool in your timeline to closed captions files in .srt, .srb and .txt format
* export generates new timecodes based on audio strips starting frames
* caption data saved to blendfile

![alt text](https://github.com/technisculpt/blender-gtts/blob/main/ui_preview.png)

* To install zip the directory "Text to Speech" and install the addon via preferences menu
* This addon will install gtts to your Blender python interpreter
* For windows users you will need to open Blender as administrator for install only, it may take a minute or two
* May not work on OSX for Blender versions before 3.0.1
* this is for educational use only!
