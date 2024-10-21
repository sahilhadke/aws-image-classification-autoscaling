import boto3
import os
from dotenv import load_dotenv
from botocore.exceptions import ClientError

# Load environment variables from .env file
load_dotenv(".env")

# Create SQS client
sqs = boto3.client('sqs', 
    region_name='us-east-1',
    aws_access_key_id=os.getenv('AWS_ACCESS_KEY'),
    aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
)
# Create the queues
req_queue_url = sqs.create_queue(QueueName='1229679960-req-queue')['QueueUrl']
res_queue_url = sqs.create_queue(QueueName='1229679960-res-queue')['QueueUrl']

print(f"req_queue_url: {req_queue_url}")
print(f"res_queue_url: {res_queue_url}")
