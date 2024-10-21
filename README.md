# aws-image-classification-autoscaling
Automated image classification using AWS infrastructure with IaaS and autoscaling. This project leverages cloud-based scalability to efficiently process and classify images, utilizing AWS services such as EC2, S3, and Auto Scaling for optimal resource management and performance.


## ASU ID - 1229679960
## Name - Sahil Yogesh Hadke
## Email - shadke1@asu.edu

#### Input Bucket: 1229679960-in-bucket
#### Output Bucket: 1229679960-out-bucket
#### Resq Queue: 1229679960-resp-queue
#### Req Queue: 1229679960-req-queue

## project1 grader
`
python3 project1_grader.py --access_keyId ACCESS_KEY --access_key SECRET_KEY
`

## P2 grader
`
python3 p2_grader.py  --access_keyId ACCESS_KEY --access_key SECRET_KEY/kyAqcMf/fL --req_sqs 1229679960-req-queue --resp_sqs 1229679960-resp-queue --in_bucket 1229679960-in-bucket --out_bucket 1229679960-out-bucket
`

## Workload gen
`
python3 workload_generator.py \
 --num_request 50 \
 --url 'http://54.144.101.120:5000/' \
 --image_folder "/Users/sahilhadke/Desktop/PROJECTS/aws-image-classification-autoscaling/CSE546-Cloud-Computing/dataset/face_images_1000" \
 --prediction_file "/Users/sahilhadke/Desktop/PROJECTS/aws-image-classification-autoscaling/resources/classification.csv"
 `