#Requires -Version 5.1
$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$WebDir = Join-Path $Root "apps\web"
$NextDir = Join-Path $WebDir ".next"

if (-not (Test-Path (Join-Path $Root "node_modules"))) {
  Write-Error "node_modules not found. Run .\scripts\setup-dev.ps1 or npm install first."
}
if (-not (Test-Path (Join-Path $WebDir ".env.local"))) {
  Write-Host "WARNING: apps/web/.env.local not found. Copy apps/web/.env.example to apps/web/.env.local" -ForegroundColor Yellow
}

# Stop any process still bound to the dev port.
Get-NetTCPConnection -LocalPort 3000 -ErrorAction SilentlyContinue |
  ForEach-Object {
    Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue
  }

Start-Sleep -Seconds 2

# Remove stale Turbopack/Webpack cache (prevents React Client Manifest errors).
if (Test-Path $NextDir) {
  Write-Host "Clearing stale .next cache..."
  Remove-Item $NextDir -Recurse -Force
}

Set-Location $WebDir
$env:NEXT_PUBLIC_ENABLE_DEV_LOGIN = "true"
$env:NEXT_TELEMETRY_DISABLED = "1"
Write-Host "Starting PlacementOS Web on http://localhost:3000"
Write-Host "Dev login enabled (email/password form on /login)"
npm run dev
