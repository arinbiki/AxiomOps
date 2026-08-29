#!/usr/bin/env powershell
# Simple PostgreSQL Start Script

Write-Host '=== Starting PostgreSQL ==='
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
Write-Host '=== Setting up Test Database ==='
Push-Location $binDir
try {
    # Create n8n database
    $createDb = & 'psql.exe' -U postgres -h localhost -p 5432 -c "CREATE DATABASE n8n;"
    if ($LASTEXITCODE -eq 0) {
        Write-Host '✅ Database "n8n" created successfully'
    } else {
        Write-Host '⚠️ Database "n8n" may already exist'
    }
    
    # Create n8n user
    $createUser = & 'psql.exe' -U postgres -h localhost -p 5432 -c "CREATE USER n8n WITH PASSWORD 'change-me';"
    if ($LASTEXITCODE -eq 0) {
        Write-Host '✅ User "n8n" created successfully'
    } else {
        Write-Host '⚠️ User "n8n" may already exist'
    }
    
    # Grant privileges
    $grantPriv = & 'psql.exe' -U postgres -h localhost -p 5432 -c "GRANT ALL PRIVILEGES ON DATABASE n8n TO n8n;"
    if ($LASTEXITCODE -eq 0) {
        Write-Host '✅ Privileges granted to user "n8n"'
    } else {
        Write-Host '⚠️ Failed to grant privileges'
    }
    
} catch {
    Write-Host '❌ Error setting up database:' $_.Exception.Message
}
Pop-Location

Write-Host ''
Write-Host '=== Test Environment Status ==='
Write-Host 'PostgreSQL setup complete.'
Write-Host ''
Write-Host 'Next steps:'
Write-Host '1. Run the test runner:'
Write-Host '   cd "d:\\web project\\AxiomOps\\Tests\\AxiomOps_Tests\\scripts"'
Write-Host '   python axiomops_production_test_runner.py'
Write-Host ''
Write-Host 'The test runner will:'
Write-Host '- Check if PostgreSQL is running'
Write-Host '- Connect to the n8n database'
Write-Host '- Run all 18 test implementation files'
Write-Host '- Generate comprehensive test reports'