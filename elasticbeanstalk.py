import boto3 as bt

beanstalk = bt.client( 'elasticbeanstalk', region_name='us-east-1' )
#---

application_name = 'etherpad'
beanstalk.create_application( ApplicationName=application_name )
beanstalk.create_application_version(
    ApplicationName='etherpad',
    VersionLabel='1',
    SourceBundle={ 'S3Bucket': 'awsinaction-code2', 'S3Key': 'chapter05/etherpad.zip' }
    )

res = beanstalk.list_available_solution_stacks()

for stack in res['SolutionStacks']:
    if 'running Node.js' in stack:
        solution_stack_name = stack
        break

print(solution_stack_name)

beanstalk.create_environment( EnvironmentName='etherpad', ApplicationName='etherpad', OptionSettings=[{'Namespace': 'aws:elasticbeanstalk:environment', 'OptionName': 'EnvironmentType', 'Value': 'SingleInstance'}] , SolutionStackName=solution_stack_name, VersionLabel='1' )

res = beanstalk.describe_environments(EnvironmentNames=['etherpad'])
print(res)

beanstalk.terminate_environment(EnvironmentName='etherpad')
beanstalk.delete_application(ApplicationName=application_name)