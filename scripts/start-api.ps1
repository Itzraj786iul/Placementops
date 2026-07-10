#Requires -Version 5.1
$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSScriptRoot
$ApiDir = Join-Path $Root "apps\api"
$Venv = Join-Path $ApiDir ".venv"
$Python = Join-Path $Venv "Scripts\python.exe"

if (-not (Test-Path $Venv)) {
  Write-Error "Virtual environment not found. Run .\scripts\setup-dev.ps1 first."
}
if (-not (Test-Path (Join-Path $ApiDir ".env"))) {
  Write-Error "apps/api/.env not found. Copy apps/api/.env.example to apps/api/.env"
}

Set-Location $ApiDir
Write-Host "Starting PlacementOS API on http://localhost:8000"
Write-Host "API docs: http://localhost:8000/docs"
& $Python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
