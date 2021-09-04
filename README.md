# blender-gtts
blender wrapper for gtts

method 1:
system wide pip install
pip install gtts
windows:
cd C:\Program Files\Blender Foundation\Blender 2.92
blender.exe --python-use-system-env
linux:
blender --python-use-system-env

method 2:
blender python pip install
from blender console:
>>> import sys
>>> sys.exec_prefix
'C:\\Program Files\\Blender Foundation\\Blender 2.92\\2.92\\python'

then in a a command prompt (windows):
cd C:\\Program Files\\Blender Foundation\\Blender 2.92\\2.92\\python\\bin
windows:
python.exe -m ensurepip
python.exe -m pip install gtts
linux:
./python -m ensurepip
./python -m pip install gtts

method 3:
run install.py from blender

method 4:
cd C:\Program Files\Blender Foundation\Blender 2.92\2.92\python\Scripts
pip.exe install gtts
