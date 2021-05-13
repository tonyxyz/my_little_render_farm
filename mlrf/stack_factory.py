import boto3
from botocore.exceptions import ClientError
from botocore.client import Config
import json
from ruamel.yaml import YAML
from ruamel.yaml.compat import StringIO
from mlrf.log import log, log_verbose

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

  # def lambda_code(self):
  #   return f'''
  #         var response = require('cfn-response');
  #         var AWS = require('aws-sdk');
  #         exports.handler = function(event, context) {{
  #           console.log("Request received:\\n", JSON.stringify(event));
  #           var physicalId = event.PhysicalResourceId;
  #           function success(data) {{
  #             return response.send(event, context, response.SUCCESS, data, physicalId);
  #           }}
  #           function failed(e) {{
  #             return response.send(event, context, response.FAILED, e, physicalId);
  #           }}
  #           // Call ec2.waitFor, continuing if not finished before Lambda function timeout.
  #           function wait(waiter) {{
  #             console.log("Waiting: ", JSON.stringify(waiter));
  #             event.waiter = waiter;
  #             event.PhysicalResourceId = physicalId;
  #             var request = ec2.waitFor(waiter.state, waiter.params);
  #             setTimeout(()=>{{
  #               request.abort();
  #               console.log("Timeout reached, continuing function. Params:\\n", JSON.stringify(event));
  #               var lambda = new AWS.Lambda();
  #               lambda.invoke({{
  #                 FunctionName: context.invokedFunctionArn,
  #                 InvocationType: 'Event',
  #                 Payload: JSON.stringify(event)
  #               }}).promise().then((data)=>context.done()).catch((err)=>context.fail(err));
  #             }}, context.getRemainingTimeInMillis() - 5000);
  #             return request.promise().catch((err)=>
  #               (err.code == 'RequestAbortedError') ?
  #                 new Promise(()=>context.done()) :
  #                 Promise.reject(err)
  #             );
  #           }}
  #           var ec2 = new AWS.EC2(),
  #               instanceId = event.ResourceProperties.InstanceId;
  #           if (event.waiter) {{
  #             wait(event.waiter).then((data)=>success({{}})).catch((err)=>failed(err));
  #           }} else if (event.RequestType == 'Create' || event.RequestType == 'Update') {{
  #             if (!instanceId) {{ failed('InstanceID required'); }}
  #             ec2.waitFor('instanceStopped', {{InstanceIds: [instanceId]}}).promise()
  #             .then((data)=>
  #               ec2.createImage({{
  #                 InstanceId: instanceId,
  #                 Name: event.RequestId
  #               }}).promise()
  #             ).then((data)=>
  #               wait({{
  #                 state: 'imageAvailable',
  #                 params: {{ImageIds: [physicalId = data.ImageId]}}
  #               }})
  #             ).then((data)=>success({{}})).catch((err)=>failed(err));
  #           }} else if (event.RequestType == 'Delete') {{
  #             if (physicalId.indexOf('ami-') !== 0) {{ return success({{}}); }}
  #             ec2.describeImages({{ImageIds: [physicalId]}}).promise()
  #             .then((data)=>
  #               (data.Images.length == 0) ? success({{}}) :
  #               ec2.deregisterImage({{ImageId: physicalId}}).promise()
  #             ).then((data)=>
  #               ec2.describeSnapshots({{Filters: [{{
  #                 Name: 'description',
  #                 Values: ["*" + physicalId + "*"]
  #               }}]}}).promise()
  #             ).then((data)=>
  #               (data.Snapshots.length === 0) ? success({{}}) :
  #               ec2.deleteSnapshot({{SnapshotId: data.Snapshots[0].SnapshotId}}).promise()
  #             ).then((data)=>success({{}})).catch((err)=>failed(err));
  #           }}
  #         }};
  #   '''

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
      ManagedPolicyArns:
        - arn:aws:iam::aws:policy/AmazonS3FullAccess
  mlrfInstanceProfile:
    Type: AWS::IAM::InstanceProfile
    Properties:
      Path: '/'
      Roles:
        - Ref: mlrfRole
  mlrfEC2LaunchTemplate:
    Type: AWS::EC2::LaunchTemplate
    DependsOn:
      - mlrfInstanceProfile
      - EC2SecurityGroup
    Properties:
      LaunchTemplateData:
        IamInstanceProfile:
          Arn: !GetAtt 'mlrfInstanceProfile.Arn'
        ImageId: {self.project_info.root_ami_id()}
        InstanceType: g3.16xlarge
        KeyName: {self.project_info.key_pair_name()}
        SecurityGroups:
        - Ref: EC2SecurityGroup
        TagSpecifications:
        - ResourceType: instance
          Tags:
          - Key: Name
            Value: My Little Render Farm Instance
        UserData:
          Fn::Base64: !Sub |
            #!/bin/bash -x
            echo "yum update" > /var/log/mlrf_log.txt
            yum update -y aws-cfn-bootstrap
            mkdir /usr/local/blender
            cd /usr/local/blender
            wget https://download.blender.org/release/Blender2.92/blender-2.92.0-linux64.tar.xz
            echo "downloaded blender" >> /var/log/mlrf_log.txt
            tar -xf ./blender-2.92.0-linux64.tar.xz
            echo "blender untarred" >> /var/log/mlrf_log.txt
  mlrfInstance:
    Type: AWS::EC2::Instance
    Properties:
      LaunchTemplate:
        LaunchTemplateId:
          Ref: mlrfEC2LaunchTemplate
        Version: 1

  EC2SecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: "EC2 security: enable SSH access"
      SecurityGroupIngress:
        - CidrIp:  0.0.0.0/0
          FromPort: '22'
          IpProtocol: tcp
          ToPort: '22'

'''
# mlrfInstance:
#     Type: AWS::EC2::Instance
#     DependsOn:
#     - mlrfEC2LaunchTemplate
#     Properties:
#       LaunchTemplate: !Ref mlrfEC2LaunchTemplate

#         InstanceMarketOptions:
#           MarketType: spot



# PolicyName: my-little-render-farm-bucket-policy
    log_verbose(f'template: {self.template}')

  def create_or_update(self):
    client = boto3.client('cloudformation')
    print('________________________________')
    print(self.template)
    print('________________________________')
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







