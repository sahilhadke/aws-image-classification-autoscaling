import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# Load environment variables from .env file
load_dotenv(".env")

# Initialize EC2 client
ec2 = boto3.client('ec2', 
    region_name='us-east-1',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

# Specify the key pair name
key_pair_name = 'cse-546-key-pair'

# Specify the AMI ID for Ubuntu 22.04
ami_id = 'ami-0a0e5d9c7acc336f1'

try:
    # Create the EC2 instance
    response = ec2.run_instances(
        ImageId=ami_id,
        MinCount=1,
        MaxCount=1,
        InstanceType='t2.micro',
        KeyName=key_pair_name,
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': 'web-instance'
                    }
                ]
            }
        ]
    )

    instance_id = response['Instances'][0]['InstanceId']
    print(f"Instance created with ID: {instance_id}")

    # Wait for the instance to be running
    waiter = ec2.get_waiter('instance_running')
    waiter.wait(InstanceIds=[instance_id])

    # Allocate an Elastic IP
    allocation_response = ec2.allocate_address(Domain='vpc')
    allocation_id = allocation_response['AllocationId']
    elastic_ip = allocation_response['PublicIp']

    # Associate the Elastic IP with your instance
    ec2.associate_address(InstanceId=instance_id, AllocationId=allocation_id)

    print(f"Elastic IP {elastic_ip} associated with instance {instance_id}")

    # Get instance details
    instance_response = ec2.describe_instances(InstanceIds=[instance_id])
    public_ip = instance_response['Reservations'][0]['Instances'][0]['PublicIpAddress']
    print(f"Instance public IP: {public_ip}")

except ClientError as e:
    print(f"An error occurred: {e}")