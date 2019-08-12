import boto3
client=boto3.client('ec2',region_name='us-east-2')
resp=client.run_instances(ImageId="ami-0ed92b56bacaf0661",InstanceType='t2.micro',MinCount=1,MaxCount=1)
for instance in resp['Instances']:
    print(instance['InstanceId'])