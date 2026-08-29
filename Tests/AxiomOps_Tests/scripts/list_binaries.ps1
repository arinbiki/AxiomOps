#!/usr/bin/env powershell
# List PostgreSQL Binaries Script

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