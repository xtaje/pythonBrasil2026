import os
import json
import boto3

SQS_ENDPOINT = os.environ.get("SQS_ENDPOINT_URL")   # localstack in dev, unset in prod
SNS_ENDPOINT = os.environ.get("SNS_ENDPOINT_URL")
QUEUE_URL = os.environ["FANOUT_QUEUE_URL"]
TOPIC_ARN = os.environ["FANOUT_TOPIC_ARN"]

sqs = boto3.client("sqs", endpoint_url=SQS_ENDPOINT)
sns = boto3.client("sns", endpoint_url=SNS_ENDPOINT)


def handler(event, context):
    for record in event["Records"]:
        body = json.loads(record["body"])
        sns.publish(TopicArn=TOPIC_ARN, Message=json.dumps(body))
        sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=json.dumps(body))
    return {"statusCode": 200}
