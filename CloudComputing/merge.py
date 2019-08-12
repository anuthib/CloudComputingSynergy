import boto3
import time
import sys
import os

# http://boto3.readthedocs.io/en/latest/reference/services/ec2.html#service-resource

ec2 = boto3.resource('ec2', region_name='us-east-2')
i = 0
# create VPC
vpc = ec2.create_vpc(CidrBlock='10.10.0.' + str(i) + '/16')
i = i + 1
# we can assign a name to vpc, or any resource, by using tag
vpc.create_tags(Tags=[{"Key": "Name", "Value": "default_vpc"}])
vpc.wait_until_available()
print(vpc.id)
ig = ec2.create_internet_gateway()
vpc.attach_internet_gateway(InternetGatewayId=ig.id)
print(ig.id)

# create subnet
subnet = ec2.create_subnet(CidrBlock='10.10.1.0/24', VpcId=vpc.id)
print(subnet.id)

# associate the route table with the subnet
subnet2 = ec2.create_subnet(CidrBlock='10.10.2.0/24', VpcId=vpc.id)
print(subnet2.id)

client = boto3.client('ec2', region_name='us-east-2')
eip_for_nat_gateway = client.allocate_address(Domain='vpc')
a = client.describe_addresses()
for b in a['Addresses']:
    print(b['AllocationId'])
c = b['AllocationId']
nat_gw = client.create_nat_gateway(SubnetId=subnet.id, AllocationId=c)
print(nat_gw['NatGateway']['NatGatewayId'])
nat_Id = nat_gw['NatGateway']['NatGatewayId']

print(nat_Id)
time.sleep(30)

route_table = vpc.create_route_table()
route = route_table.create_route(
    DestinationCidrBlock='0.0.0.0/0',
    GatewayId=ig.id
)
route_table2 = vpc.create_route_table()
route = route_table2.create_route(
    DestinationCidrBlock='0.0.0.0/0',
    NatGatewayId=nat_Id
)

print(route_table.id)
print(route_table2.id)

route_table.associate_with_subnet(SubnetId=subnet.id)
# associate the route table with the subnet
route_table2.associate_with_subnet(SubnetId=subnet2.id)

sec_group = ec2.create_security_group(
    GroupName='slice_0', Description='slice_0 sec group', VpcId=vpc.id)
sec_group.authorize_ingress(
    IpPermissions=[
        {
            'FromPort': 80,
            'ToPort': 80,
            'IpProtocol': 'tcp',
            'IpRanges': [
                {
                    'CidrIp': '0.0.0.0/0'
                }
            ]
        },
        {
            'FromPort': 22,
            'ToPort': 22,
            'IpProtocol': 'tcp',
            'IpRanges': [
                {
                    'CidrIp': '0.0.0.0/0'
                }
            ]
        },
        {
            'FromPort': 443,
            'ToPort': 443,
            'IpProtocol': 'tcp',
            'IpRanges': [
                {
                    'CidrIp': '0.0.0.0/0'
                }
            ]
        }
    ]
)
print(sec_group.id)
region='us-east-2'

outfile = open('b93.pem','w')
ec2 = boto3.client('ec2', region_name=(region))
keypair = ec2.create_key_pair(KeyName='b93')
i = keypair['KeyMaterial']
outfile.write(i)
outfile.close()
os.chmod('b93.pem', 400)

client=boto3.client('ec2',region_name='us-east-2')
instances=client.run_instances(ImageId="ami-0ed92b56bacaf0661",InstanceType='t2.micro',KeyName=keypair['KeyName'],MinCount=1,MaxCount=2,
                          NetworkInterfaces=[{'SubnetId': subnet.id, 'DeviceIndex': 0, 'AssociatePublicIpAddress': True, 'Groups': [sec_group.group_id]}])
list1=[]
for instance in instances['Instances']:
    print(instance['InstanceId'])
    list1.append(instance['InstanceId'])


ec2 = boto3.resource('ec2', region_name='us-east-2')

sec_group_load = ec2.create_security_group(
    GroupName='slice_1', Description='slice_0 sec group', VpcId=vpc.id)
sec_group_load.authorize_ingress(
    IpPermissions=[
        {
            'FromPort': 80,
            'ToPort': 80,
            'IpProtocol': 'tcp',
            'IpRanges': [
                {
                    'CidrIp': '0.0.0.0/0'
                }
            ]
        },
        {
            'FromPort': 22,
            'ToPort': 22,
            'IpProtocol': 'tcp',
            'IpRanges': [
                {
                    'CidrIp': '0.0.0.0/0'
                }
            ]
        },
    ]
)
print(sec_group_load.id)

client = boto3.client('elb')
loadbalancer = client.create_load_balancer(
    Listeners=[
        {
            'InstancePort': 80,
            'InstanceProtocol': 'HTTP',
            'LoadBalancerPort': 80,
            'Protocol': 'HTTP',
        },
    ],
    LoadBalancerName='my-load-balancer9',
    SecurityGroups=[
        sec_group_load.id,
    ],
    Subnets=[
        subnet.id,
    ],
)
print(loadbalancer)

response = client.register_instances_with_load_balancer(
    Instances=[
        {
            'InstanceId': list1[0],
        },
        {
            'InstanceId':  list1[1],
        },
    ],
    LoadBalancerName='my-load-balancer9',
)

print(response)

sec_group_private = ec2.create_security_group(
    GroupName='slice_2', Description='slice_0 sec group', VpcId=vpc.id)
sec_group_private.authorize_ingress(
    IpPermissions=[
        {
            'FromPort': 3306,
            'ToPort': 3306,
            'IpProtocol': 'tcp',
            'IpRanges': [
                {
                    'CidrIp': '0.0.0.0/0'
                }
            ]
        },
        {
            'FromPort': 22,
            'ToPort': 22,
            'IpProtocol': 'tcp',
            'IpRanges': [
                {
                    'CidrIp': '0.0.0.0/0'
                }
            ]
        },
        {
            'FromPort': 1403,
            'ToPort': 1403,
            'IpProtocol': 'tcp',
            'IpRanges': [
                {
                    'CidrIp': '0.0.0.0/0'
                }
            ]
        },
    ]
)
print(sec_group_private.id)

region='us-east-2'

outfile = open('b22.pem','w')
ec2 = boto3.client('ec2', region_name=(region))
keypair = ec2.create_key_pair(KeyName='b22')
i = keypair['KeyMaterial']
outfile.write(i)
outfile.close()
os.chmod('b22.pem', 400)

client=boto3.client('ec2',region_name='us-east-2')
instances=client.run_instances(ImageId="ami-0c979b3da41bb7d85",InstanceType='t2.micro',KeyName=keypair['KeyName'],MinCount=1,MaxCount=1,
                          NetworkInterfaces=[{'SubnetId': subnet.id, 'DeviceIndex': 0, 'AssociatePublicIpAddress': True, 'Groups': [sec_group.group_id]}])
for instance in instances['Instances']:
    print(instance['InstanceId'])

# find image id ami-835b4efa / us-west-2
# Create instance
