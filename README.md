# MedScribe AI

## Project Overview
Receives patient transcripts via API, queues them for processing, worker picks the job from queue then stores results in DynamoDB.

## Architecture
API Lambda → DynamoDB → SQS(simple service queue) → Worker Lambda(lambda) → DynamoDB

## Deployment
API Gateway URL: https://kd070ccz1b.execute-api.eu-north-1.amazonaws.com/
Stage: default

## Endpoints
- POST /jobs → submit job
- GET /jobs/{job_id} → check status
- GET /jobs → list jobs

## Testing
PowerShell scripts:
- TestMedScribeAPI.ps1
- HappyTestPath.ps1

## Permissions
Lambda IAM roles for DynamoDB, SQS, and CloudWatch
