#! bin/bash/env python3

import boto3 as bt
import paramiko

ec2 = bt.client( 'ec2', region_name='eu-central-1' )

###
#response = ec2.describe_regions()

filters = [
    {'Name': 'instance-type',
     'Values': ['t2.micro'] }
]
#response = ec2.describe_instances(Filters=filters)

filters = [
    {
        'Name': 'name',
        'Values': ['amzn-ami-hvm-*']
    }
]
#response = ec2.describe_images(Filters=filters)
#ami_id = response['Images'][0]['ImageId']
#Amazon Linux 2 AMI (HVM) - Kernel 5.10, SSD Volume Type - ami-0bd99ef9eccfee250
ami_id = 'ami-0bd99ef9eccfee250'

filters = [
    {
        'Name': 'isDefault',
        'Values': ['true']
    }
]
response = ec2.describe_vpcs(Filters=filters)
vpc_id = response['Vpcs'][0]['VpcId']

filters = [
    {
        'Name': 'vpc-id',
        'Values': [str(vpc_id)]
    }
]
response = ec2.describe_subnets(Filters=filters)
subnet_id = response['Subnets'][0]['SubnetId']

response = ec2.create_security_group(GroupName='temp_securitygroup', Description='Temp Security Group created by Boto3', VpcId=str(vpc_id))
sg_id = response['GroupId']

ec2.authorize_security_group_ingress(GroupId=sg_id, IpProtocol='tcp', FromPort=22, ToPort=22, CidrIp='0.0.0.0/0')

response = ec2.run_instances(
    ImageId=ami_id,
    KeyName='frankfurt_ec2_rsa_key',
    InstanceType='t2.micro',
    SecurityGroupIds=[sg_id],
    SubnetId=subnet_id,
    MaxCount=1,
    MinCount=1)
instance_id = response['Instances'][0]['InstanceId']

print('Waiting for EC2 to start...')
waiter = ec2.get_waiter('instance_running')
waiter.wait(InstanceIds=[instance_id])

response = ec2.describe_instances(InstanceIds=[instance_id])
publicname = response['Reservations'][0]['Instances'][0]['PublicDnsName']

# fetch id of running instance
running_instances = ec2.describe_instance_status()
instance_id = running_instances['InstanceStatuses'][0]['InstanceId']
print(instance_id)

#enter EC2 VM and run some command there
key = paramiko.RSAKey.from_private_key_file('/home/atf/.ssh/id_rsa')
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    ssh.connect(hostname=publicname, username='ec2-user', pkey=key)
    stdin, stdout, stderr = ssh.exec_command('cat /proc/loadavg')
    print( stdout.read() )
except Exception as e:
    print(e)


response = ec2.terminate_instances(InstanceIds=[instance_id])

print('Terminating EC2 Instance...')
waiter = ec2.get_waiter('instance_terminated')
waiter.wait(InstanceIds=[instance_id])

ec2.delete_security_group(GroupId=str(sg_id))

