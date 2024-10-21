from flask import Flask, request, jsonify
import csv
import boto3
import os
from dotenv import load_dotenv
import time
import base64

# Load environment variables from .env file
load_dotenv(".env")

app = Flask(__name__)

res_queue_url = 'https://sqs.us-east-1.amazonaws.com/654654563274/1229679960-res-queue'
req_queue_url = 'https://sqs.us-east-1.amazonaws.com/654654563274/1229679960-req-queue'
input_bucket = '1229679960-in-bucket'

# upload file to s3
s3 = boto3.client('s3', 
    region_name='us-east-1',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

# add the name to sqs queue
sqs = boto3.client('sqs', 
    region_name='us-east-1',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

ec2 = boto3.client('ec2', 
    region_name='us-east-1',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

ec2_resource = boto3.resource('ec2', 
    region_name='us-east-1',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)

def get_highest_instance_number():
    instances = get_running_app_instances()
    used_numbers = set()
    for instance in instances:
        for tag in instance['Tags']:
            if tag['Key'] == 'Name' and tag['Value'].startswith('app-tier-instance-'):
                try:
                    number = int(tag['Value'].split('-')[-1])
                    used_numbers.add(number)
                except ValueError:
                    continue
    
    new_number = 1
    while new_number in used_numbers:
        new_number += 1
    
    return new_number

# Get the list of running app tier instances
def get_running_app_instances():
    response = ec2.describe_instances(
        Filters=[
            {'Name': 'instance-state-name', 'Values': ['running', 'pending']},
            {'Name': 'tag:Name', 'Values': ['app-tier-instance-*']}
        ]
    )
    return [instance for reservation in response['Reservations'] for instance in reservation['Instances']]
# Load the classification lookup table
classifications = {}
with open('resources/classification.csv', 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        classifications[row[0]] = row[1]

@app.route('/health', methods=['GET'])
def hello():
    return "Hello, World2!"

def get_running_and_pending_app_instances():
    response = ec2.describe_instances(
        Filters=[
            {'Name': 'instance-state-name', 'Values': ['running', 'pending']},
            {'Name': 'tag:Name', 'Values': ['app-tier-instance-*']}
        ]
    )
    return [instance for reservation in response['Reservations'] for instance in reservation['Instances']]


@app.route('/', methods=['POST'])
def process_image():
    
    if 'inputFile' not in request.files:
        return "No file part", 400
    
    file = request.files['inputFile']

    if file.filename == '':
        return "No selected file", 400
    
    if file:
        
        filename = file.filename
        filename = filename.split(".")[0]
        
        s3.put_object(Body=file, Bucket=input_bucket, Key=filename)
        sqs.send_message(QueueUrl=req_queue_url, MessageBody=filename)
        print(f'Sent SQS message to {req_queue_url}')
        time.sleep(2)

        # Get SQS queue length
        queue_length = sqs.get_queue_attributes(
            QueueUrl=req_queue_url,
            AttributeNames=['ApproximateNumberOfMessages']
        )['Attributes']['ApproximateNumberOfMessages']

        queue_length = int(queue_length)

       
        # Get running and pending instances
        running_and_pending_instances =     ()
        current_instance_count = len(running_and_pending_instances)

        # Calculate desired instances
        max_instances = 20
        desired_instances = min(max_instances, queue_length)
        instances_to_create = max(0, desired_instances - current_instance_count)


        number_of_instances_to_create = instances_to_create


        # return "", 200

        user_data_script = '''#!/bin/bash
        mkdir /home/ubuntu/model/sahil
        source /home/ubuntu/model/venv/bin/activate
        python3 /home/ubuntu/model/polling-script.py
        '''

        # python3 /home/ubuntu/model/polling-script.py

        encoded_script = base64.b64encode(user_data_script.encode()).decode()
        if number_of_instances_to_create > 0:
            print(f"Creating {number_of_instances_to_create} new instances")
            ec2_resource.create_instances(
                ImageId='ami-0c969209666227493',
                MinCount=number_of_instances_to_create,
                MaxCount=number_of_instances_to_create,
                InstanceType='t2.micro',
                KeyName='cse-546-key-pair',
                TagSpecifications=[
                    {
                        'ResourceType': 'instance',
                        'Tags': [
                            {
                                'Key': 'Name',
                                'Value': f'app-tier-instance-{get_highest_instance_number()}'
                            },
                        ]
                    },
                ],
                UserData=encoded_script,
                IamInstanceProfile={
                    'Name': 'app-tier-roles'
                }
            )

        

        # poll the sqs queue
        while True:
            response = sqs.receive_message(
                QueueUrl=res_queue_url,
                MaxNumberOfMessages=10,
                WaitTimeSeconds=20
            )
            if 'Messages' in response:
                message = response['Messages'][0]
                if message['Body'].split(':')[0] == filename:
                    result = message['Body']
                    # delete the message
                    sqs.delete_message(
                        QueueUrl=res_queue_url,
                        ReceiptHandle=message['ReceiptHandle']
                    )
                    return result, 200
            else:
                print("No messages found. Retrying...")
                time.sleep(5)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)