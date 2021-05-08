import boto3
from botocore.exceptions import ClientError
from botocore.client import Config
import json
from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO
from mlrf.log import log, log_verbose

# Stack consists of:
#   bucket
#   batch
#   ami
#   role
#   policy

class StackFactory:
  def __init__(self, project_info):
    self.project_info = project_info
    self.create_stack_yaml()

  def get_current_user_arn(self):
    user_identity = boto3.client('sts').get_caller_identity()
    return user_identity['Arn']

  def get_current_user_name(self):
    user_identity = boto3.client('sts').get_caller_identity()
    username = user_identity['Arn'].split('/')[1]
    return username

  # def get_current_user_id(self):
  #   user_identity = boto3.client('sts').get_caller_identity()
  #   return user_identity['UserId']

  def create_stack_yaml(self):
    self.template = f'''
---
Resources:
  mlrfIOBucket:
    Type: AWS::S3::Bucket
    Properties:
      BucketName: {self.project_info.bucket_name()}
      AccessControl: Private
  mlrfRole:
    Type: AWS::IAM::Role
    Properties:
      RoleName: {self.project_info.iam_role_name()}
      AssumeRolePolicyDocument:
        Version: 2012-10-17
        Statement:
          - Effect: Allow
            Principal:
              Service: ec2.amazonaws.com
            Action:
              - sts:AssumeRole
  mlrfBucketPolicy:
    Type: AWS::IAM::Policy
    Properties:
      PolicyName: ABCD
      Roles:
        - Ref: mlrfRole
      Users:
        - {self.get_current_user_name()}
      PolicyDocument:
        Version: 2012-10-17
        Statement:
          - Effect: Allow
            Action:
              - s3:GetObject
              - s3:PutObject
            Resource:
              Fn::Join: ['', ['arn:aws:s3:::',{{Ref: mlrfIOBucket}}, '/*' ]]
'''
# PolicyName: my-little-render-farm-bucket-policy
    log_verbose(f'template: {self.template}')

  def create_or_update(self):
    client = boto3.client('cloudformation')
    try:
      response = client.validate_template(TemplateBody=self.template)
    except ClientError as error:
      log('There was an error whilst validating the stack.')
      raise error

    try:
      response = client.create_stack(
        StackName=self.project_info.stack_name(),
        TemplateBody=self.template,
        Capabilities=['CAPABILITY_NAMED_IAM']
      )
    except client.exceptions.AlreadyExistsException:
      log(f'the stack "{self.project_info.stack_name()}" already exists - skipping stack creation.')
    except ClientError as error:
      log('There was an error whilst creating the stack.')
      raise error







