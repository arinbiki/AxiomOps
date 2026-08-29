#!/usr/bin/env powershell
# PostgreSQL Installation Status Check Script

Write-Host '=== PostgreSQL Installation Status ==='
Write-Host ''

# Check if PostgreSQL service exists
$pgService = Get-Service -Name '*postgres*' -ErrorAction SilentlyContinue
if ($pgService) {
    Write-Host '✅ PostgreSQL service found:' $pgService.Name
    Write-Host '   Status: ' $pgService.Status
} else {
    Write-Host '❌ PostgreSQL service not found.'
}

Write-Host ''

# Check for PostgreSQL installation directory
$pgDir = 'C:\\Program Files\\PostgreSQL'
if (Test-Path $pgDir) {
    Write-Host '✅ PostgreSQL directory found:' $pgDir
    $items = Get-ChildItem $pgDir
    foreach ($item in $items) {
        Write-Host '   - ' $item.Name
    }
} else {
    Write-Host '❌ PostgreSQL directory not found.'
}

Write-Host ''

# Check for PostgreSQL binaries
$pgBinaries = Get-Command -Name 'pg_ctl', 'psql', 'initdb' -ErrorAction SilentlyContinue
if ($pgBinaries) {
    Write-Host '✅ PostgreSQL binaries found:'
    foreach ($binary in $pgBinaries) {
        Write-Host '   - ' $binary.Name
    }
} else {
    Write-Host '❌ PostgreSQL binaries not found.'
}

Write-Host ''
Write-Host '=== Installation Summary ==='
Write-Host 'PostgreSQL is not installed or not running on this system.'
Write-Host 'Please install PostgreSQL to run AxiomOps tests.'
Write-Host ''
Write-Host '=== Installation Instructions ==='
Write-Host '1. Download PostgreSQL from: https://www.enterprisedb.com/downloads/postgresql-windows'
Write-Host '2. Run the installer and select:"Server" and "Command Line Tools"'
Write-Host '3. Use default settings for installation directory'
Write-Host '4. Set password for postgres user during installation'
Write-Host '5. Start PostgreSQL service:'
Write-Host '   - Windows: services.msc -> PostgreSQL service -> Start'
Write-Host '   - Or run: net start postgresql'
Write-Host '6. Verify installation:'
Write-Host '   - Run: psql -U postgres'
Write-Host '   - Connect to database: postgres'