# blender-gtts
### blender wrapper for gtts

## installing gtts:
### method 1, system wide pip install:
`pip install gtts`
#### windows:
`cd C:\Program Files\Blender Foundation\Blender 2.92`
`blender.exe --python-use-system-env`
#### linux:
`blender --python-use-system-env`

### method 2 blender python pip install:
#### from blender console:
`>>> import sys`
`>>> sys.exec_prefix`
'C:\\Program Files\\Blender Foundation\\Blender 2.92\\2.92\\python'

#### then in a a command prompt (windows):
`cd C:\\Program Files\\Blender Foundation\\Blender 2.92\\2.92\\python\\bin`
`python.exe -m ensurepip`
`python.exe -m pip install gtts`

### method 3 blender python install open blender and run:
```import subprocess
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

### method 4 blender python install outside of blender (windows):
`cd C:\Program Files\Blender Foundation\Blender 2.92\2.92\python\Scripts`
`pip.exe install gtts`

## register the addon from blender by importing the zip method, or run the following script:

```
import os

if os.name == 'nt':
    dir = r'C:\\Users\marco\blender-gtts\blender-gtts.py'
    print(dir)
else:
    dir = r'/home/magagee/blender-gtts/blender-gtts.py'
    print(dir)

exec(compile(open(dir).read(), dir, 'exec'))
```