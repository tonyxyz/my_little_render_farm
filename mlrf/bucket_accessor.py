
import boto3
from botocore.exceptions import ClientError
from botocore.client import Config
from mlrf.log import log, log_verbose

class BucketAccessor:
  def __init__(self, project_info):
    self.project_info = project_info
    self.client = client = boto3.client('s3', self.project_info.region(), config=Config(s3={'addressing_style': 'path'}))

  def upload(self, file_name, object_path):
    bucket_name = self.project_info.bucket_name()
    file_path_name = self.project_info.project_root() + file_name
    object_name = object_path + file_name
    log_verbose(f'uploading "{file_path_name}" to "{bucket_name}" as "{object_name}"')
    with open(file_path_name, 'rb') as f:
      self.client.upload_fileobj(f, bucket_name, object_name)

  def upload_project(self):
    for file_name in self.project_info.project_files_local():
      self.upload(file_name, 'project/')

