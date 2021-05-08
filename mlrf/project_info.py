import os
import glob
from ruamel.yaml import YAML

class ProjectInfo:
  def __init__(self, project_file_path):
    self.project_file_path = project_file_path

    with open(self.project_file_path) as yaml_file:
      yaml = YAML()
      self.project_data = yaml.load(yaml_file)

  def save(self):
    with open(self.project_file_path, 'w') as yaml_file:
      yaml = YAML()
      yaml.dump(self.project_data, yaml_file)

  def directory(self):
    return os.path.dirname(os.path.abspath(self.project_file_path))

  def key_pair_name(self):
    return self.project_data['ami']['key_pair_name']

  def region(self):
    return self.project_data['region']

  def bucket_name(self):
    return self.project_data['bucket_name']

  def iam_role_name(self):
    return self.project_data['security']['iam_role_name']

  def iam_policy_name(self):
    return self.project_data['security']['iam_policy_name']

  def stack_name(self):
    return self.project_data['stack_name']

  def project_root(self):
    path = self.project_data['project'].get('project_root')
    if path is None:
      path = ''
    elif path[-1] != '/':
      path = path + '/'
    return path

  def project_files_local(self):
    list = [ self.project_data['project']['main_blend'] ]
    for r in self.project_data['project']['resources']:
      print(f'resource line: {self.project_root() + r}')
      for n in glob.iglob(self.project_root() + r, recursive=True):
        print(f'==="{n}"')
        list.append(n[len(self.project_root()):])
    print(list)
    return list
