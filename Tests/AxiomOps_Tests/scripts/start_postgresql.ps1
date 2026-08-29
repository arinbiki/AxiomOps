#!/usr/bin/env powershell
# Start PostgreSQL Service Script

Write-Host '=== Starting PostgreSQL Service ==='
Write-Host ''

# Try to start PostgreSQL service
try {
    $result = Start-Service -Name '*postgres*' -ErrorAction SilentlyContinue
    if ($result) {
        Write-Host '✅ PostgreSQL service started successfully'
    } else {
        Write-Host '❌ Failed to start PostgreSQL service'
    }
} catch {
    Write-Host '❌ Error starting PostgreSQL service:' $_.Exception.Message
}

Write-Host ''
Write-Host '=== Checking Service Status ==='
$services = Get-Service -Name '*postgres*' -ErrorAction SilentlyContinue
if ($services) {
    foreach ($service in $services) {
        Write-Host 'Service: ' $service.Name
        Write-Host '  Status: ' $service.Status
        Write-Host '  StartType: ' $service.StartType
        Write-Host ''
    }
} else {
    Write-Host '❌ No PostgreSQL services found.'
}

Write-Host ''
Write-Host '=== Manual Start Instructions ==='
Write-Host 'If automatic start failed, start manually:'
Write-Host '1. Open Command Prompt as Administrator'
Write-Host '2. Navigate to: C:\\Program Files\\PostgreSQL\\18\\bin'
Write-Host '3. Run: pg_ctl -D "C:\\Program Files\\PostgreSQL\\18\\data" -l logfile start'
Write-Host ''
Write-Host '=== Test Environment Status ==='
Write-Host 'After starting PostgreSQL, run the test runner:'
Write-Host 'cd "d:\\web project\\AxiomOps\\Tests\\AxiomOps_Tests\\scripts"'
Write-Host 'python axiomops_production_test_runner.py'