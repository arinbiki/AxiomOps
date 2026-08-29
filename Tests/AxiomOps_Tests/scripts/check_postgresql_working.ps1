#!/usr/bin/env powershell
# Working PostgreSQL Check Script

Write-Host '=== PostgreSQL Installation Status ==='
Write-Host ''

# Check for PostgreSQL installation
$pgDir = 'C:\\Program Files\\PostgreSQL\\18'
if (Test-Path $pgDir) {
    Write-Host '✅ PostgreSQL 18 found at:' $pgDir
    $items = Get-ChildItem $pgDir
    Write-Host 'Contents:'
    foreach ($item in $items) {
        Write-Host '  - ' $item.Name
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