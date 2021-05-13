import os
import botocore
import boto3
from mlrf.log import log, log_verbose

class KeyPairFactory:
  def __init__(self, project_info):
    self.key_pair_name = project_info.key_pair_name()
    self.project_directory = project_info.directory()

  def keyExists(self):
    exists = True
    ec2 = boto3.client('ec2')
    try:
      pairs = ec2.describe_key_pairs(KeyNames=[self.key_pair_name])
    except botocore.exceptions.ClientError as error:
      if error.response["Error"]["Code"] == 'InvalidKeyPair.NotFound':
        exists = False
      else:
        throw(error)
    return exists

  def create_and_save_key_pair(self):
    ec2 = boto3.resource('ec2')
    pem_filename = os.path.join(self.project_directory, f'{self.key_pair_name}.pem')
    log_verbose(f'will create key pair: {pem_filename}')

    with open(pem_filename,'w') as outfile:
      key_pair = ec2.create_key_pair(KeyName=self.key_pair_name)
      keyPairOut = str(key_pair.key_material)
      outfile.write(keyPairOut)
      log(f'saved key pair to {pem_filename}')
