#!/usr/bin/env powershell
# Analyze PostgreSQL Installation Script

Write-Host '=== PostgreSQL Installation Analysis ==='
Write-Host ''

# Check PostgreSQL installation
$pgDir = 'C:\\Program Files\\PostgreSQL\\18'
if (Test-Path $pgDir) {
    Write-Host '✅ PostgreSQL 18 found at:' $pgDir
    $items = Get-ChildItem $pgDir
    Write-Host 'Contents:'
    foreach ($item in $items) {
        Write-Host '  - ' $item.Name
        if ($item.PSIsContainer) {
            Write-Host '    (Directory)'
            
            # Check if this is a data directory
            if ($item.Name -eq 'data') {
                Write-Host '    -> This is likely the data directory'
                $dataFiles = Get-ChildItem $item.FullName
                Write-Host '    Database files in data directory:'
                foreach ($file in $dataFiles) {
                    Write-Host '      - ' $file.Name
                }
            }
        } else {
            Write-Host '    (File)'
        }
    }
    
    # Check for data directory specifically
    $dataDir = $pgDir + '\\data'
    if (Test-Path $dataDir) {
        Write-Host ''
        Write-Host '✅ Data directory found:' $dataDir
        $dataFiles = Get-ChildItem $dataDir
        Write-Host 'Database files:'
        foreach ($file in $dataFiles) {
            Write-Host '  - ' $file.Name
        }
    } else {
        Write-Host ''
        Write-Host '❌ Data directory not found.'
        Write-Host 'This means PostgreSQL needs to be initialized with a data directory.'
        Write-Host ''
        Write-Host 'To initialize PostgreSQL:'
        Write-Host '1. Open Command Prompt as Administrator'
        Write-Host '2. Navigate to: C:\\Program Files\\PostgreSQL\\18\\bin'
        Write-Host '3. Run: initdb -D "C:\\Program Files\\PostgreSQL\\18\\data"'
        Write-Host '4. Then start PostgreSQL: pg_ctl -D "C:\\Program Files\\PostgreSQL\\18\\data" -l logfile start'
    }
} else {
    Write-Host '❌ PostgreSQL directory not found.'
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
Write-Host 'PostgreSQL is not properly installed or configured.'
Write-Host 'Please install PostgreSQL properly:'
Write-Host '1. Download from: https://www.enterprisedb.com/downloads/postgresql-windows'
Write-Host '2. Run installer with:"Server" and "Command Line Tools"'
Write-Host '3. Use default settings'
Write-Host '4. Set password for postgres user'
Write-Host '5. Start PostgreSQL service'
Write-Host ''
Write-Host 'After proper installation, run the test runner:'
Write-Host 'cd "d:\\web project\\AxiomOps\\Tests\\AxiomOps_Tests\\scripts"'
Write-Host 'python axiomops_production_test_runner.py'