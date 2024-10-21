import boto3
import time
import os
from face_recognition import face_match
import requests

def get_instance_id():
    # Step 1: Get the token for IMDSv2
    token_url = "http://169.254.169.254/latest/api/token"
    headers = {'X-aws-ec2-metadata-token-ttl-seconds': '21600'}  # Token TTL of 6 hours
    try:
        token_response = requests.put(token_url, headers=headers)
        token_response.raise_for_status()  # Raise an error for bad responses
        token = token_response.text

        # Step 2: Use the token to get the instance ID
        instance_id_url = "http://169.254.169.254/latest/meta-data/instance-id"
        instance_id_response = requests.get(instance_id_url, headers={'X-aws-ec2-metadata-token': token})
        
        if instance_id_response.status_code == 200:
            return instance_id_response.text
        else:
            return "Error: Unable to retrieve instance ID"
    except requests.RequestException as e:
        return f"Error: {e}"

# Initialize SQS, S3, and EC2 clients
sqs = boto3.client('sqs', region_name='us-east-1')
s3 = boto3.client('s3', region_name='us-east-1')
ec2 = boto3.client('ec2', region_name='us-east-1')

req_queue_url = 'https://sqs.us-east-1.amazonaws.com/654654563274/1229679960-req-queue'
res_queue_url = 'https://sqs.us-east-1.amazonaws.com/654654563274/1229679960-resp-queue'
input_bucket = '1229679960-in-bucket'
output_bucket = '1229679960-out-bucket'

def process_image(image_path):
    # Your image processing logic (placeholder)
    print(f'image_key input: {image_path}')
    try:
        result = face_match(image_path, '/home/ubuntu/model/data.pt')
        # result = "DEFAULT"
    except Exception as e:
        print(f'Cannot predict')
        print(e)
        result = ["ERROR"]
    return result[0]

def terminate_instance():
    # Terminate current instance
    instance_id = get_instance_id()
    print(f'Terminating')
    ec2.terminate_instances(InstanceIds=[instance_id])
   
def poll_and_process():
    while True:
        # Poll the request queue for messages
        response = sqs.receive_message(QueueUrl=req_queue_url)
        
        if 'Messages' in response:
            # Process the message
            message = response['Messages'][0]
            image_key = message['Body']

            print(f'image_key: {image_key}')
            print(f'message: {response['Messages'][0]}')

            
            # Delete the message from the queue
            receipt_handle = message['ReceiptHandle']
            sqs.delete_message(QueueUrl=req_queue_url, ReceiptHandle=receipt_handle)

            # Download the file from S3 and store it in EC2
            try:

                s3.download_file(input_bucket, image_key, f"/home/ubuntu/model/input_images/{image_key}.jpg")
                print(f'file downloaded')

            except Exception as e:
                print(f'Error downloading file: {e}')

            name_predicted = process_image(f"/home/ubuntu/model/input_images/{image_key}.jpg")
        
            s3.put_object(
                Bucket=output_bucket,
                Key=image_key,
                Body=name_predicted
            )


            print(f'name_predicted: {name_predicted}')
            # add message to response queue
            result_in_queue = f'{image_key}:{name_predicted}'
            sqs.send_message(QueueUrl=res_queue_url, MessageBody=result_in_queue)
            print(f'sent to queue')
        else:
            print(f'Terminating...')
            # Terminate instance if request queue is empty
            terminate_instance()
            return

        time.sleep(5)  # Poll every 5 seconds

# Start polling and processing
poll_and_process()
