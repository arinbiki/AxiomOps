#!/usr/bin/env powershell
# Initialize PostgreSQL Script

Write-Host '=== PostgreSQL Initialization ==='
Write-Host ''

# Check if PostgreSQL is properly installed
$pgDir = 'C:\\Program Files\\PostgreSQL\\18'
if (-not (Test-Path $pgDir)) {
    Write-Host '❌ PostgreSQL directory not found.'
    Write-Host 'Please install PostgreSQL properly.'
    exit 1
}

# Check for bin directory
$binDir = $pgDir + '\\bin'
if (-not (Test-Path $binDir)) {
    Write-Host '❌ PostgreSQL bin directory not found.'
    Write-Host 'Please install PostgreSQL properly.'
    exit 1
}

# Check for data directory
$dataDir = $pgDir + '\\data'
if (Test-Path $dataDir) {
    Write-Host '✅ Data directory already exists:' $dataDir
    $dataFiles = Get-ChildItem $dataDir
    Write-Host 'Database files:'
    foreach ($file in $dataFiles) {
        Write-Host '  - ' $file.Name
    }
} else {
    Write-Host '❌ Data directory not found.'
    Write-Host 'Initializing PostgreSQL...'
    
    # Initialize PostgreSQL
    Push-Location $binDir
    try {
        $initResult = & 'initdb.exe' -D $dataDir
        if ($LASTEXITCODE -eq 0) {
            Write-Host '✅ PostgreSQL initialized successfully'
        } else {
            Write-Host '❌ Failed to initialize PostgreSQL'
            exit 1
        }
    } catch {
        Write-Host '❌ Error initializing PostgreSQL:' $_.Exception.Message
        exit 1
    }
    Pop-Location
}

# Start PostgreSQL
Write-Host ''
Write-Host '=== Starting PostgreSQL ==='
Push-Location $binDir
try {
    $startResult = & 'pg_ctl.exe' -D $dataDir -l logfile start
    if ($LASTEXITCODE -eq 0) {
        Write-Host '✅ PostgreSQL started successfully'
    } else {
        Write-Host '❌ Failed to start PostgreSQL'
        Write-Host 'Check logfile for details'
    }
} catch {
    Write-Host '❌ Error starting PostgreSQL:' $_.Exception.Message
}
Pop-Location

# Check service status
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

# Check if PostgreSQL is running
Write-Host ''
Write-Host '=== Testing PostgreSQL Connection ==='
try {
    $testConn = psql -U postgres -h localhost -p 5432 -c "SELECT 1"
    if ($LASTEXITCODE -eq 0) {
        Write-Host '✅ PostgreSQL is running and accessible'
    } else {
        Write-Host '❌ PostgreSQL is not accessible'
    }
} catch {
    Write-Host '❌ Error testing PostgreSQL connection:' $_.Exception.Message
}

Write-Host ''
Write-Host '=== Test Environment Status ==='
Write-Host 'PostgreSQL initialization complete.'
Write-Host ''
Write-Host 'Next steps:'
Write-Host '1. Create the "n8n" database:'
Write-Host '   psql -U postgres -c "CREATE DATABASE n8n;"'
Write-Host '2. Create the "n8n" user:'
Write-Host '   psql -U postgres -c "CREATE USER n8n WITH PASSWORD 'change-me';"'
Write-Host '3. Grant privileges:'
Write-Host '   psql -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE n8n TO n8n;"'
Write-Host ''
Write-Host 'After setting up the database, run the test runner:'
Write-Host 'cd "d:\\web project\\AxiomOps\\Tests\\AxiomOps_Tests\\scripts"'
Write-Host 'python axiomops_production_test_runner.py'