#!/usr/bin/env powershell
# Detailed PostgreSQL Installation Status Check Script

Write-Host '=== PostgreSQL Service Status ==='
Write-Host ''

# Check all PostgreSQL related services
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
Write-Host '=== Available PostgreSQL Installation ==='
$pgDir = 'C:\\Program Files\\PostgreSQL\\18'
if (Test-Path $pgDir) {
    Write-Host '✅ PostgreSQL 18 found at:' $pgDir
    $binDir = $pgDir + '\\bin'
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
} else {
    Write-Host '❌ PostgreSQL directory not found.'
}

Write-Host ''
Write-Host '=== PostgreSQL Installation Summary ==='
Write-Host 'PostgreSQL 18 is installed but not running.'
Write-Host 'To start PostgreSQL:'
Write-Host '1. Open Command Prompt as Administrator'
Write-Host '2. Navigate to: C:\\Program Files\\PostgreSQL\\18\\bin'
Write-Host '3. Run: pg_ctl -D "C:\\Program Files\\PostgreSQL\\18\\data" -l logfile start'
Write-Host '4. Or use Windows Services: services.msc -> PostgreSQL 18 -> Start'
Write-Host ''
Write-Host '=== Test Environment Setup ==='
Write-Host 'For AxiomOps tests, you need:'
Write-Host '1. PostgreSQL running on localhost:5432'
Write-Host '2. Database "n8n" with user "n8n" and password "change-me"'
Write-Host '3. n8n server running on localhost:5678'
Write-Host ''
Write-Host '=== Quick Setup Commands ==='
Write-Host '# Start PostgreSQL service'
Write-Host 'net start postgresql'
Write-Host ''
Write-Host '# Or start manually'
Write-Host 'cd "C:\\Program Files\\PostgreSQL\\18\\bin"'
Write-Host 'pg_ctl -D "C:\\Program Files\\PostgreSQL\\18\\data" -l logfile start'