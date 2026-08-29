#!/usr/bin/env powershell
# Check Services Script

Write-Host '=== Available Services ==='
Write-Host ''

# Get all services and filter for PostgreSQL
$allServices = Get-Service
$pgServices = $allServices | Where-Object { $_.Name -like '*postgres*' -or $_.DisplayName -like '*postgres*' -or $_.Name -like '*postgresql*' -or $_.DisplayName -like '*postgresql*' }

if ($pgServices) {
    Write-Host 'Found PostgreSQL services:'
    foreach ($service in $pgServices) {
        Write-Host '  - ' $service.Name ' (' $service.DisplayName ')'
        Write-Host '    Status: ' $service.Status
        Write-Host '    StartType: ' $service.StartType
        Write-Host ''
    }
} else {
    Write-Host '❌ No PostgreSQL services found.'
    Write-Host ''
    Write-Host 'All services:'
    $allServices | ForEach-Object { Write-Host '  - ' $_.Name ' (' $_.DisplayName ')' }
}

Write-Host ''
Write-Host '=== PostgreSQL Installation ==='
$pgDir = 'C:\\Program Files\\PostgreSQL\\18'
if (Test-Path $pgDir) {
    Write-Host '✅ PostgreSQL 18 found at:' $pgDir
    $dataDir = $pgDir + '\\data'
    if (Test-Path $dataDir) {
        Write-Host '✅ Data directory found:' $dataDir
        $dataFiles = Get-ChildItem $dataDir
        Write-Host 'Database files:'
        foreach ($file in $dataFiles) {
            Write-Host '  - ' $file.Name
        }
    } else {
        Write-Host '❌ Data directory not found.'
        Write-Host 'Data directory path:' $dataDir
    }
} else {
    Write-Host '❌ PostgreSQL directory not found.'
}

Write-Host ''
Write-Host '=== Test Environment Status ==='
Write-Host 'To start PostgreSQL manually:'
Write-Host '1. Open Command Prompt as Administrator'
Write-Host '2. Navigate to: C:\\Program Files\\PostgreSQL\\18\\bin'
Write-Host '3. Run: pg_ctl -D "C:\\Program Files\\PostgreSQL\\18\\data" -l logfile start'
Write-Host ''
Write-Host 'After starting PostgreSQL, run the test runner:'
Write-Host 'cd "d:\\web project\\AxiomOps\\Tests\\AxiomOps_Tests\\scripts"'
Write-Host 'python axiomops_production_test_runner.py'