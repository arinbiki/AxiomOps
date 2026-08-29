#!/usr/bin/env powershell
# Final PostgreSQL Check Script

Write-Host '=== PostgreSQL Installation Check ==='
Write-Host ''

# Check for PostgreSQL installation
$pgDir = 'C:\\Program Files\\PostgreSQL\\18'
if (Test-Path $pgDir) {
    Write-Host '✅ PostgreSQL 18 found at:' $pgDir
    
    # Check for data directory
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
        
        # List all directories in PostgreSQL folder
        Write-Host ''
        Write-Host 'Available directories in PostgreSQL folder:'
        $items = Get-ChildItem $pgDir
        foreach ($item in $items) {
            Write-Host '  - ' $item.Name
        }
    }
} else {
    Write-Host '❌ PostgreSQL directory not found.'
}

Write-Host ''
Write-Host '=== PostgreSQL Bin Directory ==='
$binDir = 'C:\\Program Files\\PostgreSQL\\18\\bin'
if (Test-Path $binDir) {
    Write-Host '✅ Bin directory found:' $binDir
    $binaries = Get-ChildItem $binDir
    Write-Host 'Available binaries:'
    foreach ($binary in $binaries) {
        Write-Host '  - ' $binary.Name
    }
} else {
    Write-Host '❌ Bin directory not found.'
}

Write-Host ''
Write-Host '=== PostgreSQL Service Status ==='
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
Write-Host '=== Test Environment Status ==='
Write-Host 'To start PostgreSQL manually:'
Write-Host '1. Open Command Prompt as Administrator'
Write-Host '2. Navigate to: C:\\Program Files\\PostgreSQL\\18\\bin'
Write-Host '3. Run: pg_ctl -D "C:\\Program Files\\PostgreSQL\\18\\data" -l logfile start'
Write-Host ''
Write-Host 'After starting PostgreSQL, run the test runner:'
Write-Host 'cd "d:\\web project\\AxiomOps\\Tests\\AxiomOps_Tests\\scripts"'
Write-Host 'python axiomops_production_test_runner.py'