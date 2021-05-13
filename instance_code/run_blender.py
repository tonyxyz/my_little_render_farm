import os
import subprocess

first_frame = os.environ.get('TSNQ_FIRST_FRAME', '1')
last_frame = os.environ.get('TSNQ_LAST_FRAME', '1')
engine = os.environ.get('TSNQ_ENGINE', 'CYCLES')
blend_file = os.environ.get('TSNQ_BLEND_FILE', 'episode.blend')
blender_path = os.environ.get('TSNQ_BLENDER_PATH', 'blender')

this_path = os.path.abspath(__file__)
init_py = str(os.path.join(this_path, 'blender_init.py'))

command = [ blender_path,
  '-b', blend_file, '-s', first_frame, '-e', last_frame,
  '-E', engine, '-P', init_py,
  '-a'
]
# , '-P', 'blender_init.py'
print(f' "{command}" ')
subprocess.run(command)
# for instance:
# export TSNQ_BLENDER_PATH=/Applications/Blender.app/Contents/MacOS/Blender&&\
# export TSNQ_BLEND_FILE=/Volumes/MyDisc/MyProject/myproject.blend&&\
# export TSNQ_FIRST_FRAME=10&&\
# export TSNQ_LAST_FRAME=12&&\
# export TSNQ_BUCKET_NAME=my-little-render-farm-files&&\
# python instance_code/run_blender.py
