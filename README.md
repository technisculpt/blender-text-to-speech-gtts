# blender-gtts
### blender wrapper for gtts (google text to speech)
### make audio captions quickly
### convert closed captions files to audio
### support included for .srt, .srb and .txt files
### .txt files with no timecodes will sort the audio strips based on length

![alt text](https://github.com/technisculpt/blender-gtts/blob/main/preview.png)

## installing gtts:

### You will need to install gtts. Your options are to install python, pip and gtts and run blender using the system python environment, or to install gtts within blenders python environment

### method 1, system wide:
`pip install gtts`
#### windows, locate app:
`cd C:\Program Files\Blender Foundation\Blender 2.93`
`blender.exe --python-use-system-env`
##### you can avoid changing directory by modifying the PATH on windows 10
##### using the 'edit the system environment variables' control panel, -> advanced -> environment variables -> System variables, edit path and add the blender directory
#####

#### on linux PATH is already set:
`blender --python-use-system-env`

### If it worked you should be able to open a python console from within blender and not recieve an error when typing:
`import gtts`

### method 2 blender python pip install:
#### open blender and run the following script
```
import subprocess
import sys
import os
 
# path to python.exe
python_exe = os.path.join(sys.prefix, 'bin', 'python.exe')
 
# upgrade pip
subprocess.call([python_exe, "-m", "ensurepip"])
subprocess.call([python_exe, "-m", "pip", "install", "--upgrade", "pip"])
 
# install required packages
subprocess.call([python_exe, "-m", "pip", "install", "gtts"])
```

### restart blender, if that didn't work you can try:
#### from blender console:
`>>> import sys`

`>>> sys.exec_prefix`

'C:\\Program Files\\Blender Foundation\\Blender 2.92\\2.92\\python'

#### then in a a command prompt (windows):
`cd C:\\Program Files\\Blender Foundation\\Blender 2.92\\2.92\\python\\bin`

`python.exe -m ensurepip`

`python.exe -m pip install gtts`

### restart blender, if that didn't work you can try:
`cd C:\Program Files\Blender Foundation\Blender 2.92\2.92\python\Scripts`

`pip.exe install gtts`

### to find your blender location, open blender and a python console and type:
```
import os
print(os.sys.path)
```
## Register the addon from blender in preferences->addons, or run the following script from blender:

```
import os

if os.name == 'nt': # windows
    dir = r'C:\\Users\marco\blender-gtts\blender-gtts.py'
else: # linux and mac os x
    dir = r'/home/magagee/blender-gtts/blender-gtts.py'

exec(compile(open(dir).read(), dir, 'exec'))
```
