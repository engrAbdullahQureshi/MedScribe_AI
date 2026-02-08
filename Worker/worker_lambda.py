import json
import boto3
import time
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.client('dynamodb', region_name='eu-north-1')
sqs = boto3.client('sqs', region_name='eu-north-1')

def lambda_handler(event, context):
    for record in event['Records']:
        message = json.loads(record['body'])
        job_id = message['job_id']
        start_time = time.time()
        logger.info(f"Worker started: job_id={job_id}")
        try:
            # Simulate processing
            result = f"Processed transcript for {job_id}"
            time.sleep(2)

            # Update DynamoDB (fixed reserved keyword issue)
            dynamodb.update_item(
                TableName='MedScribeJobs',
                Key={'job_id': {'S': job_id}},
                UpdateExpression="SET #s=:s, #r=:r, completed_at=:c",
                ExpressionAttributeNames={
                    '#s': 'status',
                    '#r': 'result'   # alias for reserved keyword
                },
                ExpressionAttributeValues={
                    ':s': {'S': 'completed'},
                    ':r': {'S': result},
                    ':c': {'S': time.strftime('%Y-%m-%dT%H:%M:%SZ')}
                }
            )

            duration = time.time() - start_time
            logger.info(f"Worker completed: job_id={job_id}, duration={duration:.2f}s, status=success")
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"Worker failed: job_id={job_id}, duration={duration:.2f}s, error={str(e)}")
