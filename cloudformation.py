import boto3 as bt

ec2 = bt.client( 'ec2', region_name='eu-central-1' )
cf = bt.client( 'cloudformation', region_name='eu-central-1' )
#------

res = ec2.describe_vpcs()
VpcId = res['Vpcs'][0]['VpcId']

res = ec2.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [VpcId]}])
SubnetId = res['Subnets'][0]['SubnetId']

stack_name = 'vpn'

res = cf.create_stack(
    StackName=stack_name,
    TemplateURL='https://s3.amazonaws.com/awsinaction-code2/chapter05/vpn-cloudformation.yaml',
    Parameters=[{
        'ParameterKey': 'KeyName',
        'ParameterValue': 'frankfurt_ec2_rsa_key'
    }, {
        'ParameterKey': 'VPC',
        'ParameterValue': VpcId
    }, {
        'ParameterKey': 'Subnet',
        'ParameterValue': SubnetId
    }, {
        'ParameterKey': 'IPSecSharedSecret',
        'ParameterValue': 'shared_secret'
    }, {
        'ParameterKey': 'VPNUser',
        'ParameterValue': 'vpn'
    }, {
        'ParameterKey': 'VPNPassword',
        'ParameterValue': 'password'
    }]
)

waiter = cf.get_waiter('stack_create_complete')
waiter.wait(StackName=stack_name)
print('Stack Created')

res = cf.delete_stack(StackName=stack_name)
waiter = cf.get_waiter('stack_delete_complete')
print('Stack Deleted')