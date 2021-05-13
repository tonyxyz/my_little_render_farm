import bpy
import subprocess
import os
from bpy.app.handlers import persistent



@persistent
def frame_save_handler(scene):
  print(f"frame save handler: {scene.render.frame_path()}")
  bucket = os.environ.get('TSNQ_BUCKET_NAME', '')
  if bucket is not '':
    subprocess.run(['aws', 's3', 'cp', scene.render.frame_path(), 's3://' + bucket])

def setup_cycles_cuda():

  prop = bpy.context.preferences.addons['cycles'].preferences
  prop.get_devices()
  prop.compute_device_type = 'CUDA'

  for device in prop.devices:
    if device.type == 'CUDA':
      device.use = True
  bpy.context.scene.cycles.device = 'GPU'

  for scene in bpy.data.scenes:
    scene.cycles.device = 'GPU'

def setup_post_frame_handler():
  bpy.app.handlers.render_write.append(frame_save_handler)

setup_cycles_cuda()
setup_post_frame_handler()
