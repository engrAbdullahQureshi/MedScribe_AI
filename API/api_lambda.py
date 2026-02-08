import json
import boto3
import uuid
import time
import logging

# Setup logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.client('dynamodb', region_name='eu-north-1')
sqs = boto3.client('sqs', region_name='eu-north-1')

QUEUE_URL = 'https://sqs.eu-north-1.amazonaws.com/318276049007/MedScribeQueue'
TABLE_NAME = 'MedScribeJobs'

def lambda_handler(event, context):
    method = event['requestContext']['http']['method']
    path = event['requestContext']['http']['path']
    
    logger.info(f"API called: method={method}, path={path}")

    if method == 'POST' and path == '/jobs':
        body = json.loads(event['body'])
        transcript = body.get('transcript')
        if not transcript:
            logger.warning("POST /jobs failed: transcript missing")
            return {'statusCode':400, 'body':json.dumps({'error':'transcript required'})}
        
        job_id = f"job_{str(uuid.uuid4())[:8]}"
        created_at = time.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        # Insert job into DynamoDB
        dynamodb.put_item(
            TableName=TABLE_NAME,
            Item={
                'job_id': {'S': job_id},
                'transcript': {'S': transcript},
                'status': {'S': 'pending'},
                'created_at': {'S': created_at},
                'completed_at': {'S': ''},
                'result': {'S': ''},
                'error': {'S': ''}
            }
        )
        
        # Push job_id to SQS
        sqs.send_message(QueueUrl=QUEUE_URL, MessageBody=json.dumps({'job_id': job_id}))
        
        logger.info(f"Job created: job_id={job_id}, status=pending")
        return {'statusCode':200, 'body':json.dumps({'job_id': job_id, 'status':'pending'})}
    
    elif method == 'GET':
        if path.startswith('/jobs/'):
            job_id = path.split('/')[-1]
            resp = dynamodb.get_item(
                TableName=TABLE_NAME,
                Key={'job_id': {'S': job_id}}
            )
            if 'Item' not in resp:
                logger.warning(f"GET /jobs/{job_id} failed: job not found")
                return {'statusCode':404, 'body':json.dumps({'error':'Job not found'})}
            item = resp['Item']
            logger.info(f"Job fetched: job_id={job_id}, status={item['status']['S']}")
            return {'statusCode':200, 'body':json.dumps({
                'job_id': item['job_id']['S'],
                'status': item['status']['S'],
                'result': item.get('result', {}).get('S', ''),
                'error': item.get('error', {}).get('S', '')
            })}
        elif path == '/jobs':
            qs = event.get('queryStringParameters') or {}
            status = qs.get('status', 'pending')
            limit = int(qs.get('limit', 10))
            resp = dynamodb.scan(
                TableName=TABLE_NAME,
                Limit=limit,
                FilterExpression='#s = :status',
                ExpressionAttributeNames={'#s':'status'},
                ExpressionAttributeValues={':status': {'S': status}}
            )
            jobs = [{'job_id': i['job_id']['S'], 'status': i['status']['S']} for i in resp.get('Items',[])]
            logger.info(f"List jobs called: status={status}, returned={len(jobs)}")
            return {'statusCode':200, 'body':json.dumps(jobs)}
    
    logger.warning("Route not found")
    return {'statusCode':404, 'body':json.dumps({'error':'Route not found'})}
