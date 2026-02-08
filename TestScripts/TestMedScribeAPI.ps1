$API = "https://kd070ccz1b.execute-api.eu-north-1.amazonaws.com"

Write-Host "--- SUBMIT NEW JOB ---"
$submitResponse = Invoke-RestMethod -Method POST "$API/jobs" `
    -Headers @{ "Content-Type" = "application/json" } `
    -Body '{ "transcript": "Patient reports mild headache for 1 day." }'

Write-Host "Response:"
$submitResponse | ConvertTo-Json
$jobId = $submitResponse.job_id

Write-Host "`n--- GET JOB STATUS ---"
if ($jobId) {
    $statusResponse = Invoke-RestMethod -Method GET "$API/jobs/$jobId"
    $statusResponse | ConvertTo-Json
} else {
    Write-Host "No job_id returned from POST."
}

Write-Host "`n--- LIST PENDING JOBS ---"
$listResponse = Invoke-RestMethod -Method GET "$API/jobs?status=pending&limit=5"
$listResponse | ConvertTo-Json
