import os
import botocore
import boto3

class KeyPairFactory:
  def __init__(self, project_info):
    self.key_pair_name = project_info.key_pair_name()
    self.project_directory = project_info.directory()

  def keyExists(self):
    exists = True
    ec2 = boto3.client('ec2')
    try:
      pairs = ec2.describe_key_pairs(KeyNames=[self.key_pair_name])
      print(f'key pairs: #{pairs}')
    except botocore.exceptions.ClientError as error:
      if error.response["Error"]["Code"] == 'InvalidKeyPair.NotFound':
        print("the key pair does not exist")
        exists = False
      else:
        throw(error)
    return exists

  def create_and_save_key_pair(self):
    ec2 = boto3.resource('ec2')
    pem_filename = os.path.join(self.project_directory, f'{self.key_pair_name}.pem')

    with open(pem_filename,'w') as outfile:
      key_pair = ec2.create_key_pair(KeyName=self.key_pair_name)
      keyPairOut = str(key_pair.key_material)
      outfile.write(keyPairOut)
