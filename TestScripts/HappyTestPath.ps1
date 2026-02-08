# Phase 7 - Happy Path Test

# API base URL (without /dev if default stage)
$API = "https://kd070ccz1b.execute-api.eu-north-1.amazonaws.com"

Write-Host "--- SUBMIT NEW JOB ---"
$submitResponse = Invoke-RestMethod -Method POST "$API/jobs" `
    -Headers @{ "Content-Type" = "application/json" } `
    -Body '{ "transcript": "Patient reports mild headache for 1 day." }'

$submitResponse | ConvertTo-Json -Depth 5
$jobId = $submitResponse.job_id
Write-Host "`nJob ID submitted:" $jobId

Start-Sleep -Seconds 5   # Wait a few seconds for processing

Write-Host "`n--- GET JOB STATUS ---"
$jobStatus = Invoke-RestMethod -Method GET "$API/jobs/$jobId"
$jobStatus | ConvertTo-Json -Depth 5
