import os
import boto3
from botocore.exceptions import ClientError
from botocore.client import Config
from mlrf.log import log, log_verbose

class BucketAccessor:
  def __init__(self, project_info):
    self.project_info = project_info
    self.client = client = boto3.client('s3', self.project_info.region(), config=Config(s3={'addressing_style': 'path'}))

  def upload(self, file_name, source_path, object_path):
    bucket_name = self.project_info.bucket_name()
    file_path_name =  os.path.join(source_path, file_name)
    object_name = object_path + file_name
    log_verbose(f'uploading "{file_path_name}" to "{bucket_name}" as "{object_name}"')
    with open(file_path_name, 'rb') as f:
      self.client.upload_fileobj(f, bucket_name, object_name)

  def upload_project(self):
    for file_name in self.project_info.project_files_local():
      self.upload(file_name, self.project_info.project_root(), 'project/')

  def upload_instance_code(self):
    this_path = os.path.abspath(__file__)

    instance_code_dir = os.path.abspath(os.path.join(os.path.dirname(this_path), '..', 'instance_code'))
    files = [f for f in os.listdir(instance_code_dir) if os.path.isfile(os.path.join(instance_code_dir, f))]
    for f in files:
      self.upload(f, instance_code_dir, 'instance_code/')


