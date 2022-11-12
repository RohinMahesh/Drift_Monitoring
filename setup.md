# S3

- This monitoring service utilizes S3 to store HTML artifacts to host a static webpage for drift monitoring
- The object (index.html file from Evidently AI) will be served via the S3 bucket, and this object will then
turn into a website by enabling static hosting
- Once you have a dedicated S3 bucket, the following steps are performed:
    1. Under Properties, Static website hosting is enabled
        1.1 Under "Index document", index.html is selected
        1.2 Under "Error document", error.html is selected
    2. Bucket policy is defined to correctly serve out traffic:
        2.1 In your bucket under Permissions, the following is defined under Bucket policy:
        ```bash
        {
            "Version":“2012-10-17”,
            "Statement":[
                {
                    "Sid":"PublicReadGetObject",
                    "Effect":"Allow",
                    "“Principal":"*",
                    "Action":[
                        "“s3":"GetObject”"
                    ],
                    "Resource":[
                        "arn:aws:s3:::example.com/*”
                    ]
                }
            ]
        }
        ```
        2.2 A key point to note is that the bucket policy above will allow anyone to access the static
            webpage. This is for development purposes and is not ideal for production use
        2.3 In the bucket policy, modify Resource for your specific static webpage

# Lambda

- The drift detection is executed using Lambda, which is a serverless function
- The Lambda function is containerized using Docker, and the respective Docker image is registered in (ECR). 
- Once the Container image is selected, under Trigger configuration:
    1. Select EventBridge (CloudWatch Events). This will be used to schedule the execution via Cron
    2. If you do not have an existing rule, create a new rule, and schedule the following expression:
       ```bash
       cron(30 9 * * MON)
       ```

# ECR

- Elastic Container Registry (ECR) is used to manage the Docker images used in this monitoring service
- Using the Dockerfile located in the Drift_Monitoring folder, build the Docker image:

```bash
docker build -t drift_monitor:v1 .
```

- To create and run a Docker container:

```bash
docker run -it --rm \
    -p 8080:8080 \
    -e AWS_SECRET_KEY_ID=”YOUR_KEY” \
    -e AWS_SECRET_ACCESS_KEY=”YOUR_SECRET”\
    -e AWS_DEFAULT_REGION=”REGION” \
    drift_monitor:v1
```

- Once the Docker image is built, create an ECR repository:

```bash
aws ecr create-repository –repository-name drift_monitoring
```

- Push this Docker image to the repositoryUri provided when creating the ECR repository and create a Lambda function via 
  Container image using the REMOTE_IMAGE:

```bash
REMOTE_URI= “” 
REMOTE_TAG=”v1”
REMOTE_IMAGE=${REMOTE_URI}:${REMOTE_TAG}

LOCAL_IMAGE=”drift_monitor:v1”
docker tag ${LOCAL_IMAGE} ${REMOTE_IMAGE}
docker push ${REMOTE_IMAGE}
```

# SNS

- In addition to the static webpage, it is critical to alert the Data Science team of the drift status
- Create a topic and the subsequent subscription:
    1. Set Protocol as "Email"
    2. Set Endpoint as the Data Science team service email ID
- Under your drift_lambda.py script, inside lambda_handler:
    1. Modify your SNS boto3 client using your AWS credentials
        1.1 It is recommended to use a key vault service like AWS KMS to manage your keys
    2. Modify TargetArn using your SNS topic
- In addition to the static webpage, a JSON representation of the individual covariate drift status
  will be emailed to the Data Science service account email
