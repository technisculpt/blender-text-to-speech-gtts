import os

if os.name == 'nt':
    dir = r'C:\\Users\marco\blender-gtts\blender-gtts.py'
    print(dir)
else:
    dir = r'/home/magagee/blender-gtts/blender-gtts.py'
    print(dir)

exec(compile(open(dir).read(), dir, 'exec'))
