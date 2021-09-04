# blender-gtts
blender wrapper for gtts

pip install gtts
cd C:\Program Files\Blender Foundation\Blender 2.92
blender.exe --python-use-system-env

or from blender console:
>>> import sys
>>> sys.exec_prefix
'C:\\Program Files\\Blender Foundation\\Blender 2.92\\2.92\\python'

then in a shell:

cd C:\\Program Files\\Blender Foundation\\Blender 2.92\\2.92\\python\\bin
windows:
python.exe -m ensurepip
python.exe -m pip install gTTS
linux:
./python -m ensurepip
./python -m pip install gTTS

or try running install.py

or try
cd C:\Program Files\Blender Foundation\Blender 2.92\2.92\python\Scripts
pip.exe install gtts
pip3.exe install gtts